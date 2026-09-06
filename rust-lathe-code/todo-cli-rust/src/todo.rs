use chrono::{DateTime, Local};
use colored::Colorize;
use serde::{Deserialize, Serialize};
use std::fmt;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Todo {
    pub id: u32,                     // id值
    pub content: String,             // 待办内容
    pub completed: bool,             // 是否完成
    pub created_at: DateTime<Local>, // 创建日期
    #[serde(default)]
    pub priority: u8, // 待办的重要程度 0-普通，默认颜色；1-高，黄色；2-紧急，红色
    #[serde(default)]
    pub completed_at: Option<DateTime<Local>>,
    #[serde(default)]
    pub tags: Vec<String>, // 标签
}
impl Todo {
    pub fn new(id: u32, content: String, priority: u8, tags: Vec<String>) -> Self {
        // let now = chrono::Local::now().format("%Y-%m-%d %H:%M").to_string();
        Todo {
            id,
            content,
            completed: false,
            created_at: Local::now(),
            priority,
            completed_at: None, // 新建时没有完成时间
            tags,
        }
    }
}

impl fmt::Display for Todo {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let status = if self.completed { "✅" } else { "⭕" };
        let priority_label = match self.priority {
            2 => "!!",
            1 => "!",
            _ => " ",
        };
        let tags_label = if self.tags.is_empty() {
            String::new()
        } else {
            format!(" [{}]", self.tags.join(", "))
        };
        write!(
            f,
            "[{}] {} {} {}{}",
            self.id, status, priority_label, self.content, tags_label,
        )
    }
}

impl From<&str> for Todo {
    fn from(value: &str) -> Self {
        Todo {
            id: 0,
            content: value.to_string(),
            completed: false,
            created_at: Local::now(),
            priority: 0,
            completed_at: None,
            tags: vec![],
        }
    }
}

pub fn print_todos(label: &str, items: &[&Todo]) {
    if items.is_empty() {
        println!("Nothing here.");
        return;
    }
    println!("  {} ({})", label, items.len());
    for t in items {
        let priority_tag = match t.priority {
            2 => format!("  {}", "!!urgent".red().bold()),
            1 => format!("  {}", "! high".yellow()),
            _ => String::new(),
        };
        let tags_info = if t.tags.is_empty() {
            String::new()
        } else {
            format!("{}", t.tags.join("/").cyan())
        };
        if t.completed {
            let completed_time = match &t.completed_at {
                Some(time) => format!(" ({})", time.format("%Y-%m-%d %H:%M").to_string()),
                None => String::new(),
            };
            println!(
                "   {} {} {}  {}{} ({}){}",
                format!("[{}]", t.id).dimmed(),
                tags_info,
                t.content.strikethrough(),
                "✔ done".green(),
                completed_time.red(),
                t.created_at.format("%Y-%m-%d %H:%M"),
                priority_tag,
            );
        } else {
            println!(
                "   [{}] {} {} ({}){}",
                t.id,
                tags_info,
                t.content,
                t.created_at.format("%Y-%m-%d %H:%M"),
                priority_tag,
            );
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn todo_equality() {
        let ts = Local::now();
        let a = Todo {
            id: 1,
            content: "买菜".to_string(),
            completed: false,
            created_at: ts,
            priority: 0,
            completed_at: None,
            tags: vec![],
        };
        let b = Todo {
            id: 1,
            content: "买菜".to_string(),
            completed: false,
            created_at: ts,
            priority: 0,
            completed_at: None,
            tags: vec![],
        };
        assert_eq!(a, b);
    }
}

#[test]
fn todo_from_str() {
    let todo = Todo::from("买菜");
    assert_eq!(todo.content, "买菜");
    assert_eq!(todo.id, 0);
    assert_eq!(todo.priority, 0);
    assert!(!todo.completed);
    assert!(todo.tags.is_empty());

    // Into 也能用
    let todo2: Todo = "写周报".into();
    assert_eq!(todo2.content, "写周报");
}
