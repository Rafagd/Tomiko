use sea_orm_migration::prelude::*;
use macros::wait;

macro_rules! bigint_not_null (
    ($table:ident :: $field:ident) => {{ 
        ColumnDef::new($table::$field)
            .big_integer()
            .not_null()
    }}
);

macro_rules! bigint_not_null_pk (
    ($table:ident :: $field:ident) => {{ 
        bigint_not_null!($table::$field)
            .primary_key()
    }}
);

macro_rules! string_not_null (
    ($table:ident :: $field:ident) => {{ 
        ColumnDef::new($table::$field)
            .string()
            .not_null()
    }}
);

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        wait! {
            manager.create_table(
                Table::create()
                    .table(Chat::Table)
                    .if_not_exists()
                    .col(bigint_not_null_pk!(Chat::Id))
                    .col(string_not_null!(Chat::Type))
                    .col(string_not_null!(Chat::Title))
                    .take() // .to_owned()
            )
        }?;

        wait! {
            manager.create_table(
                Table::create()
                    .table(Message::Table)
                    .if_not_exists()
                    .col(bigint_not_null_pk!(Message::Id))
                    .col(bigint_not_null!(Message::UserId))
                    .col(bigint_not_null!(Message::ChatId))
                    .col(string_not_null!(Message::Text))
                    .col(
                        ColumnDef::new(Message::SentAt)
                            .date_time()
                            .not_null()
                    )
                    .col(
                        ColumnDef::new(Message::EditedAt)
                            .date_time()
                            .null()
                    )
                    .take() // .to_owned()
            )
        }?;

        wait! {
            manager.create_table(
                Table::create()
                    .table(Update::Table)
                    .if_not_exists()
                    .col(bigint_not_null_pk!(Update::Id))
                    .take() // .to_owned()
            )
        }?;

        wait! {
            manager.create_table(
                Table::create()
                    .table(User::Table)
                    .if_not_exists()
                    .col(bigint_not_null_pk!(User::Id))
                    .col(
                        ColumnDef::new(User::IsBot)
                            .boolean()
                            .not_null()
                    )
                    .col(string_not_null!(User::FirstName))
                    .col(string_not_null!(User::LastName))
                    .col(string_not_null!(User::UserName))
                    .take() // .to_owned()
            )
        }
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        wait! { manager.drop_table(Table::drop().table(Chat::Table).to_owned()) }?;
        wait! { manager.drop_table(Table::drop().table(Message::Table).to_owned()) }?;
        wait! { manager.drop_table(Table::drop().table(Update::Table).to_owned()) }?;
        wait! { manager.drop_table(Table::drop().table(User::Table).to_owned()) }?;
        Ok(())
    }
}

/// Learn more at https://docs.rs/sea-query#iden
#[derive(Iden)]
enum Chat {
    Table,
    Id,
    Type,
    Title,
}

#[derive(Iden)]
enum Message {
    Table,
    Id,
    UserId,
    ChatId,
    Text,
    SentAt,
    EditedAt,
}

#[derive(Iden)]
enum Update {
    Table,
    Id,
}

#[derive(Iden)]
enum User {
    Table,
    Id,
    IsBot,
    FirstName,
    LastName,
    UserName,
}
