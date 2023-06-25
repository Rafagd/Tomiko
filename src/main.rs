use std::{fmt::Display, time::Duration};

use chrono::{DateTime, Utc, TimeZone};
use tokio::{ io::{AsyncReadExt}, fs::File,  };
use tomiko::{config::Config, wait, telegram::{ Telegram, request::{GetMe, GetUpdates}, TelegramError }};
use toml;

fn msg<Tz>(date: &DateTime<Tz>, user: &str, text: &str, is_edit: bool)
    where
        Tz: TimeZone,
        Tz::Offset: Display
{
    let edit_msg = if is_edit { "Edit: " } else { "" };
    println!("[{}] <{}> {}{}", date.format("%H:%M"), user, edit_msg, text);
}

#[tokio::main]
#[allow(unreachable_code)]
async fn main() -> ::std::result::Result<(), TelegramError>
{
    let config_str = {
        let mut config_file = wait!{ File::open("data/config.toml") }
            .expect("Could not open config file");

        let mut config_str = String::new();
        wait! { config_file.read_to_string(&mut config_str) }
            .expect("Could not read config file");

        config_str
    };

    let config: Config = toml::from_str(&config_str)
        .expect("Could not parse config file");

    let telegram = Telegram::new(&config.telegram.api_token);
    let bot_data = wait!{ GetMe{}.execute(&telegram) }
        .expect("Could not fetch bot data");

    let bot_name = bot_data.first_name;
    msg(&Utc::now(), &bot_name, "Bot initialized", false);

    let mut last_update_id = 872009694;
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
        
        for update in updates {
            last_update_id = update.update_id;

            let username = if update.message.from.username.is_empty() {
                &update.message.from.first_name
            } else {
                &update.message.from.username
            };

            let date = match update.message.date {
                Some(date) => date,
                None => { panic!("{:#?}", update); },
            };
            msg(&date, username, &update.message.text, update.message.edit_date.is_some());
        }

        let sleep_ms = if cfg!(debug_assertions) { 1000 } else { 5000 };
        wait! { tokio::time::sleep(Duration::from_millis(sleep_ms)) };
    }

    unreachable!("This should not be reached!");
    Ok(())
}
