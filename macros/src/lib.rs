#[macro_export]
macro_rules! wait {
    ( $($tt: tt)* ) => {{
        { $($tt)* }.await
    }}
}

