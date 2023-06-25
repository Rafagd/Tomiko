#[macro_export]
macro_rules! wait {
    ( $($tt: tt)* ) => {{
        { $($tt)* }.await
    }}
}

pub mod config;
pub mod telegram;
