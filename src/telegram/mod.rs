use std::{error::Error, fmt::Debug};
use macros::wait;

pub mod request;
pub mod response;

#[derive(Debug)]
pub struct Telegram
{
    api_url: String,
}

impl Telegram
{
    pub fn new(api_token: &str) -> Self
    {
        Self {
            api_url: String::from("https://api.telegram.org/bot") + api_token,
        }
    }

    pub async fn execute(&self, request: request::Request) -> Result<response::Response, TelegramError>
    {
        let client = reqwest::ClientBuilder::new()
            .build()
            .expect("Could not build HTTP Client");

        let response = wait! {
            client.post(format!("{}/{}", self.api_url, request.action))
                .json::<request::Parameters>(&request.parameters)
                .send()
        };
        let response = match response {
            Ok(r)  => r,
            Err(e) => {
                println!("Request: {:#?}", request);
                println!("Error: {:#?}", e);
                panic!("Error sending request!");
            },
        };

        let response = match wait!{ response.text() } {
            Ok(r)  => r,
            Err(e) => {
                println!("Request: {:#?}", request);
                println!("Error: {:#?}", e);
                panic!("Error fetching response!");
            },
        };

        let parsed_response = serde_json::from_str::<serde_json::Value>(&response);
        let response = match parsed_response {
            Ok(r) => r,
            Err(e) => {
                println!("Response: {:#?}", response);
                println!("Error: {:#?}", e);
                panic!("Error parsing response!");
            },
        };

        let converted_response = response::Response::from_value(&request.action, &response);
        let response = match converted_response {
            Ok(r) => r,
            Err(e) => {
                println!("Response: {:#?}", response);
                println!("Error: {:#?}", e);
                panic!("Error converting response!");
            },
        };

        if !response.ok {
            return Err(TelegramError::NotOk);
        }

        Ok(response)
    }
}
    
#[derive(Debug)]
pub enum TelegramError
{
    BoxedError(Box<dyn Error>),
    NotOk,
    UnexpectedResult(response::Result),
}
