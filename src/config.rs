use serde::Deserialize;

#[derive(Debug, Deserialize)]
pub struct Config {
    pub telegram: Telegram,
}

#[derive(Debug, Deserialize)]
pub struct Telegram {
    pub api_token: String,
}

