use std::result::Result as StdResult;
use super::{response::{Me, Result, Update, Message}, Telegram, TelegramError};
use macros::wait;

#[derive(Debug, serde::Serialize)]
pub struct Request
{
    pub action:     String,
    pub parameters: Parameters,
}

#[derive(Debug, serde::Serialize)]
#[serde(untagged)]
pub enum Parameters
{
    GetMe,
    GetUpdates(GetUpdates),
    SendMessage(SendMessage),
}

pub struct GetMe;

impl GetMe
{
    pub async fn execute(self, telegram: &Telegram) -> StdResult<Me, TelegramError>
    {
        let response = wait! {
            telegram.execute(Request {
                action:     String::from("getMe"),
                parameters: Parameters::GetMe,
            })
        }?;

        match response.result {
            Result::GetMe(me) => Ok(me),
            e => Err(TelegramError::UnexpectedResult(e)),
        }
    }
}

#[derive(Debug, serde::Serialize, Default)]
pub struct GetUpdates
{ 
    pub offset:  Option<i64>,
    pub limit:   Option<u8>,
    pub timeout: Option<usize>,
    pub allowed_updates: Option<Vec<String>>,
}

impl GetUpdates
{
    pub async fn execute(self, telegram: &Telegram) -> StdResult<Vec<Update>, TelegramError>
    {
        let response = wait ! {
            telegram.execute(Request {
                action:     String::from("getUpdates"),
                parameters: Parameters::GetUpdates(self),
            })
        }?;

        match response.result {
            Result::GetUpdates(updates) => Ok(updates),
            e => Err(TelegramError::UnexpectedResult(e)),
        }
    }
}

#[derive(Debug, serde::Serialize, Default)]
pub struct SendMessage
{
    pub chat_id: i64,
    pub text:    String,
    pub reply_to_message_id: Option<i64>,
}

impl SendMessage
{
    pub async fn execute(self, telegram: &Telegram) -> StdResult<Message, TelegramError>
    {
        let response = wait ! {
            telegram.execute(Request {
                action:     String::from("sendMessage"),
                parameters: Parameters::SendMessage(self),
            })
        }?;

        match response.result {
            Result::SendMessage(message) => Ok(message),
            e => Err(TelegramError::UnexpectedResult(e)),
        }
    }
}
