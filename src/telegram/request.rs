use std::result::Result as StdResult;
use super::{response::{Me, Result, Update}, Telegram, TelegramError};

#[derive(Debug, serde::Serialize)]
pub struct Request
{
    pub action:     String,
    pub parameters: Parameters,
}

impl Request
{
    pub fn get_me() -> Self
    {
        Request {
            action:     String::from("getMe"),
            parameters: Parameters::GetMe,
        }
    }

    pub fn get_updates(offset: Option<i64>, limit: Option<u8>, timeout: Option<usize>, allowed_updates: Option<Vec<String>>) -> Self
    {
        Request {
            action: String::from("getUpdates"),
            parameters: Parameters::GetUpdates(
                GetUpdates {
                    offset,
                    limit, 
                    timeout,
                    allowed_updates,
                }
            ),
        }
    }
}

#[derive(Debug, serde::Serialize)]
#[serde(untagged)]
pub enum Parameters
{
    GetMe,
    GetUpdates(GetUpdates),
}

pub struct GetMe;

impl GetMe
{
    pub async fn execute(self, telegram: &Telegram) -> StdResult<Me, TelegramError>
    {
        let response = wait! { telegram.execute(Request::get_me()) }?;
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
            telegram.execute(Request::get_updates(
                self.offset,
                self.limit,
                self.timeout,
                self.allowed_updates,
            ))
        }?;

        match response.result {
            Result::GetUpdates(updates) => Ok(updates),
            e => Err(TelegramError::UnexpectedResult(e)),
        }
    }
}
