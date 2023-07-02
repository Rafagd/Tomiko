use std::{ fmt, error::Error, result::Result as StdResult };

use chrono::{ DateTime, TimeZone, Utc };
use serde_json::Value;

#[derive(Debug)]
pub enum ResponseError
{
    Unimplemented(String),
    Unexpected(Value),
}
impl Error for ResponseError {}

impl fmt::Display for ResponseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:#?}", self)
    }
}

#[derive(Debug)]
pub struct Response
{
    pub ok:     bool,
    pub result: Result,
}

impl Response
{
    pub fn from_value(action: &str, value: &Value) -> StdResult<Response, ResponseError>
    {
        let Some(ok) = value.get("ok") else {
            return Err(ResponseError::Unexpected(value.clone()));
        };

        let Some(ok) = ok.as_bool() else {
            return Err(ResponseError::Unexpected(value.clone()));
        };

        let Some(result) = value.get("result") else {
            return Err(ResponseError::Unexpected(value.clone()));
        };

        let result = Result::from_value(action, result)?;

        Ok(Response {
            ok,
            result,
        })
    }
}

#[derive(Debug)]
pub enum Result
{
    None,
    GetMe(Me),
    GetUpdates(Vec<Update>),
    SendMessage(Message),
}

impl Result
{
    fn from_value(action: &str, value: &Value) -> StdResult<Self, ResponseError>
    {
        let result = match action {
            "getMe"      => Result::GetMe(Me::from_value(value)),
            "getUpdates" => Result::GetUpdates(match value.as_array() {
                Some(array) => array.iter().map(|update| Update::from_value(update)).collect(),
                None        => vec![],
            }),
            "sendMessage" => Result::SendMessage(Message::from_value(value)),
            action => {
                return Err(ResponseError::Unimplemented(String::from(action)));
            }
        };

        Ok(result)
    }
} 

#[derive(Debug, Default)]
pub struct Me
{
    pub can_join_groups: bool,
    pub can_read_all_group_messages: bool,
    pub first_name: String,
    pub id: u64,
    pub is_bot: bool,
    pub supports_inline_queries: bool,
    pub username: String,
}

impl Me
{
    fn from_value(value: &Value) -> Self
    {
        Self {
            can_join_groups: {
                value.get("can_join_groups")
                    .map(|v| v.as_bool().unwrap_or(false))
                     .unwrap_or(false)
            },

            can_read_all_group_messages: {
                value.get("can_read_all_group_messages")
                    .map(|v| v.as_bool().unwrap_or(false))
                    .unwrap_or(false)
            },

            first_name: {
                value.get("first_name")
                    .map(|v| v.as_str().unwrap_or(""))
                    .unwrap_or("")
                    .to_string()
            },

            id: {
                value.get("id")
                    .map(|v| v.as_u64().unwrap_or(0))
                    .unwrap_or(0)
            },

            is_bot: {
                value.get("is_bot")
                    .map(|v| v.as_bool().unwrap_or(false))
                    .unwrap_or(false)
            },

            supports_inline_queries: {
                value.get("supports_inline_queries")
                    .map(|v| v.as_bool().unwrap_or(false))
                    .unwrap_or(false)
            },

            username: {
                value.get("username")
                    .map(|v| v.as_str().unwrap_or(""))
                    .unwrap_or("")
                    .to_string()
            },
        }
    }
}

#[derive(Debug)]
pub struct Update
{
    pub id:      i64,
    pub message: Message,
}

impl Update
{
    fn from_value(value: &Value) -> Self
    {
        let message = match value.get("message") {
            Some(message) => message, 
            None => match value.get("edited_message") {
                Some(message) => message,
                None => { panic!("{:#?}", value); },
            },
        };
        let message = Message::from_value(&message);

        Self {
            id: {
                value.get("update_id")
                    .map(|v| v.as_i64().unwrap_or(0))
                    .unwrap_or(0)
            },

            message,
        }
    }
}



#[derive(Debug, Default)]
pub struct Message
{
    pub id:   i64,
    pub from: User,
    pub chat: Chat,

    pub date:      Option<DateTime<Utc>>,
    pub edit_date: Option<DateTime<Utc>>,

    pub text: String,
}

impl Message
{
    fn from_value(value: &Value) -> Self
    {
        Self {
            id: {
                value.get("message_id")
                    .map(|v| v.as_i64().unwrap_or(0))
                    .unwrap_or(0)
            },

            from: match value.get("from") {
                Some(v) => User::from_value(&v),
                None    => User::default(),
            },

            chat: match value.get("chat") {
                Some(v) => Chat::from_value(&v),
                None    => Chat::default(),
            },

            date: match value.get("date") {
                Some(v) => match v.as_i64() {
                    Some(timestamp) => Utc.timestamp_opt(timestamp, 0).single(),
                    None => None,
                },
                _ => None,
            },

            edit_date: match value.get("edit_date") {
                Some(v) => match v.as_i64() {
                    Some(timestamp) => Utc.timestamp_opt(timestamp, 0).single(),
                    None => None,
                },
                _ => None,
            },

            text: {
                value.get("text")
                    .map(|v| v.as_str().unwrap_or(""))
                    .unwrap_or("")
                    .to_string()
            },

        }
    }
}

#[derive(Debug, Default)]
pub struct User
{
    pub id:     i64,
    pub is_bot: bool,
    pub first_name: String,
    pub last_name:  String,
    pub user_name:  String,
}

impl User
{
    fn from_value(value: &Value) -> Self
    {
        Self {
            id: {
                value.get("id")
                    .map(|v| v.as_i64().unwrap_or(0))
                    .unwrap_or(0)
            },

            is_bot: {
                value.get("is_bot")
                    .map(|v| v.as_bool().unwrap_or(false))
                    .unwrap_or(false)
            },

            first_name: {
                value.get("first_name")
                    .map(|v| v.as_str().unwrap_or(""))
                    .unwrap_or("")
                    .to_string()
            },

            last_name: {
                value.get("last_name")
                    .map(|v| v.as_str().unwrap_or(""))
                    .unwrap_or("")
                    .to_string()
            },

            user_name: {
                value.get("username")
                    .map(|v| v.as_str().unwrap_or(""))
                    .unwrap_or("")
                    .to_string()
            },
        }
    }
}

#[derive(Debug, Default)]
pub struct Chat
{
    pub id:    i64,
    pub title: String,

    pub chat_type: String,
}

impl Chat
{
    fn from_value(value: &Value) -> Self
    {
        Self {
            id: {
                value.get("id")
                    .map(|v| v.as_i64().unwrap_or(0))
                    .unwrap_or(0)
            },

            title: {
                value.get("title")
                    .map(|v| v.as_str().unwrap_or(""))
                    .unwrap_or("")
                    .to_string()
            },

            chat_type: {
                value.get("type")
                    .map(|v| v.as_str().unwrap_or(""))
                    .unwrap_or("")
                    .to_string()
            },
        }
    }
}
