use std::{fmt::Display, time::Duration, collections::HashMap };

use chrono::{DateTime, Utc, TimeZone };
use tokio::{ io::AsyncReadExt, fs::File };
use tomiko::{config::Config, telegram::{ Telegram, request::{GetMe, GetUpdates, SendMessage}, TelegramError }, entity};
use toml;
use rand::Rng;
use sea_orm::{ Database, DatabaseConnection, EntityTrait, sea_query::OnConflict, DbBackend };
use macros::wait;
use migration::{ Migrator, MigratorTrait };
use dotenvy::dotenv;


fn msg<Tz>(date: &DateTime<Tz>, user: &str, text: &str, is_edit: bool)
    where
        Tz: TimeZone,
        Tz::Offset: Display
{
    let edit_msg = if is_edit { "Edit: " } else { "" };
    println!("[{}] <{}> {}{}", date.format("%H:%M"), user, edit_msg, text);
}

async fn load_config() -> Config
{
    let config_file = option_env!("CONFIG_FILE").unwrap_or("data/config.toml");

    let config_str = {
        let mut config_file = wait!{ File::open(config_file) }
            .expect("Could not open config file");

        let mut config_str = String::new();
        wait! { config_file.read_to_string(&mut config_str) }
            .expect("Could not read config file");

        config_str
    };

    toml::from_str(&config_str)
        .expect("Could not parse config file")
}

async fn connect_to_database()  -> DatabaseConnection
{
    dotenv().expect(".env file not found");

    let db_url  = dotenvy::var("DATABASE_URL").expect("DATABASE_URL env not set");
    let db_conn = wait! { Database::connect(db_url) }
        .expect("Could not connect to database");

    wait! { Migrator::up(&db_conn, None) }
        .expect("Problem during migration");

    db_conn
}

#[tokio::main]
#[allow(unreachable_code)]
async fn main() -> ::std::result::Result<(), TelegramError>
{
    let config = wait! { load_config() };

    let telegram = Telegram::new(&config.telegram.api_token);
    let bot_data = wait!{ GetMe{}.execute(&telegram) }
        .expect("Could not fetch bot data");

    let db_conn = wait! { connect_to_database() };

    let bot_name = bot_data.first_name;
    msg(&Utc::now(), &bot_name, "Bot initialized", false);

    let mut last_update_id = 0;
    loop {
        let updates = wait!{
            GetUpdates {
                offset: Some(last_update_id + 1),
                limit:  Some(100),
                ..Default::default()
            }.execute(&telegram)
        };

        let updates = match updates {
            Ok(me) => me,
            Err(e) => { return Err(e); },
        };
        
        let mut rng = rand::thread_rng();

        let mut updates_dbo  = HashMap::new();
        let mut chats_dbo    = HashMap::new();
        let mut users_dbo    = HashMap::new();
        let mut messages_dbo = HashMap::new();

        for update in updates {
            last_update_id = update.id;

            let update_dbo: entity::update::ActiveModel = entity::update::Model {
                id: update.id,
            }.into();
            updates_dbo.insert(update.id, update_dbo);

            let chat_dbo: entity::chat::ActiveModel = entity::chat::Model {
                id:     update.message.chat.id,
                r#type: update.message.chat.chat_type,
                title:  update.message.chat.title,
            }.into();
            chats_dbo.insert(update.message.chat.id, chat_dbo);

            let user_dbo: entity::user::ActiveModel = entity::user::Model {
                id:         update.message.from.id,
                is_bot:     update.message.from.is_bot,
                first_name: update.message.from.first_name,
                last_name:  update.message.from.last_name,
                user_name:  update.message.from.user_name,
            }.into();
            users_dbo.insert(update.message.from.id, user_dbo);

            let message_dbo: entity::message::ActiveModel = entity::message::Model {
                id:        update.message.id,
                chat_id:   update.message.chat.id,
                user_id:   update.message.from.id,
                text:      update.message.text,
                sent_at:   update.message.date.unwrap().naive_utc(),
                edited_at: update.message.edit_date.map(|d| d.naive_utc()),
            }.into();
            messages_dbo.insert(update.message.id, message_dbo);
            
            let rand_value = rng.gen::<f32>();
            if rand_value < 1. {// 0.01 {
                let random_msg = wait! {
                    entity::message::Entity::find()
                        .from_raw_sql(sea_orm::Statement {
                            sql: String::from("SELECT * FROM message TABLESAMPLE SYSTEM(10) ORDER BY RANDOM() LIMIT 1"),
                            values: None,
                            db_backend: DbBackend::Postgres,
                        })
                        .all(&db_conn)
                }.expect("Error feching random message");

                if random_msg.len() > 0 {
                    msg(&Utc::now(), "Betamiko", &random_msg[0].text, false);
                }
                /*
                wait! {
                    SendMessage {
                        chat_id: update.message.chat.id,
                        text:    String::from("Random Message"),
                        reply_to_message_id: Some(update.message.id),
                        ..Default::default()
                    }.execute(&telegram)
                }.expect("Could not send message!");
                */
            }
        }

        if updates_dbo.len() > 0 {
            let update_result = wait!{ 
                entity::update::Entity::insert_many(updates_dbo.into_values())
                    .on_conflict(
                        OnConflict::column(entity::update::Column::Id)
                            .do_nothing()
                            .to_owned()
                    )
                    .exec(&db_conn)
            };
            if let Err(e) = update_result {
                println!("{:#?}", e);
                panic!("Could not save updates!");
            }
        }

        if messages_dbo.len() > 0 {
            let message_result = wait! {
                entity::message::Entity::insert_many(messages_dbo.into_values())
                    .on_conflict(
                        OnConflict::column(entity::message::Column::Id)
                            .update_column(entity::message::Column::EditedAt)
                            .to_owned()
                    )
                    .exec(&db_conn)
            };
            if let Err(e) = message_result {
                println!("{:#}", e);
                panic!("Could not save messages!");
            }
        }

        if users_dbo.len() > 0 {
            let user_result = wait!{ 
                entity::user::Entity::insert_many(users_dbo.into_values())
                    .on_conflict(
                        OnConflict::column(entity::user::Column::Id)
                            .update_columns([
                                entity::user::Column::FirstName,
                                entity::user::Column::LastName,
                                entity::user::Column::UserName,
                            ])
                            .to_owned()
                    )
                    .exec(&db_conn)
            };
            if let Err(e) = user_result {
                println!("{:#}", e);
                panic!("Could not save users!");
            }
        }
        
        if chats_dbo.len() > 0 {
            let chat_result = wait!{ 
                entity::chat::Entity::insert_many(chats_dbo.into_values())
                    .on_conflict(
                        OnConflict::column(entity::chat::Column::Id)
                            .update_column(entity::chat::Column::Title)
                            .to_owned()
                    )
                    .exec(&db_conn)
            };
            if let Err(e) = chat_result {
                println!("{:#}", e);
                panic!("Could not save chats!");
            }
        }

        let sleep_ms = if cfg!(debug_assertions) { 1000 } else { 5000 };
        wait! { tokio::time::sleep(Duration::from_millis(sleep_ms)) };
    }

    unreachable!("This should not be reached!");
    Ok(())
}
