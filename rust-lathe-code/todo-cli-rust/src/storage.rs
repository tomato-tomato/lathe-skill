use anyhow::{Context, Result};
use std::fs;
use std::path::PathBuf;

use crate::todo::Todo;

fn data_file(custom_dir: Option<&PathBuf>) -> PathBuf {
    let dir = match custom_dir {
        Some(d) => d.clone(),
        None => dirs::config_dir()
            .expect("Cannot determine config directory")
            .join("tasky"),
    };
    fs::create_dir_all(&dir).expect("Cannot create config directory");
    dir.join("todos.json")
}

pub fn load_todos(custom_dir: Option<&PathBuf>) -> Result<Vec<Todo>> {
    let path = data_file(custom_dir);
    if !path.exists() {
        return Ok(Vec::new());
    }
    let content = fs::read_to_string(&path).context("Failed to read todos file")?;
    let todos: Vec<Todo> = serde_json::from_str(&content).unwrap_or_default();
    Ok(todos)
}

pub fn save_todos(todos: &[Todo], custom_dir: Option<&PathBuf>) -> Result<()> {
    let path = data_file(custom_dir);
    let json = serde_json::to_string_pretty(todos).context("Failed to serialize todos")?;
    fs::write(&path, json).context("Failed to write todos file")?;
    Ok(())
}

// 单元测试
#[cfg(test)]
mod tests {
    use super::*;
    use chrono::Local;

    #[test]
    fn save_and_load_roundtrip() {
        // 准备测试数据
        let todos = vec![
            Todo {
                id: 1,
                content: "测试任务一".to_string(),
                completed: false,
                created_at: Local::now(),
                priority: 0,
                completed_at: None,
                tags: vec!["test".to_string()],
            },
            Todo {
                id: 2,
                content: "测试任务二".to_string(),
                completed: true,
                created_at: Local::now(),
                priority: 2,
                completed_at: Some(Local::now()),
                tags: vec![],
            },
        ];

        // 写入。该测试会直接写入真实的json文件中
        save_todos(&todos, None).expect("save should succeed");

        // 读回
        let loaded = load_todos(None).expect("load should succeed");

        // 验证
        assert_eq!(loaded.len(), 2);
        assert_eq!(loaded[0].id, 1);
        assert_eq!(loaded[0].content, "测试任务一");
        assert_eq!(loaded[0].priority, 0);
        assert!(loaded[0].tags.contains(&"test".to_string()));
        assert_eq!(loaded[1].id, 2);
        assert!(loaded[1].completed);
        assert_eq!(loaded[1].priority, 2);
        assert!(loaded[1].completed_at.is_some());
    }

    #[test]
    fn load_default_does_not_crash() {
        // 冒烟测试：验证 load_todos(None) 能正常运行而不崩溃
        // 因为 load_todos(None) 指向默认路径，文件可能存在也可能不存在
        // （save_and_load_roundtrip 测试已在此前写入了数据文件）
        // 所以这里只验证函数能正常返回 Result，不检查具体内容
        let loaded = load_todos(None);
        assert!(loaded.is_ok());
    }
}
