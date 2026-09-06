use anyhow::Result;
use chrono::Local;
use clap::Parser;
use colored::Colorize;

mod cli;
mod commands;
mod storage;
mod todo;

use cli::{Cli, Commands};
use commands::cmd_stats;
use storage::{load_todos, save_todos};
use todo::{Todo, print_todos};

fn cmd_add(todos: &mut Vec<Todo>, content: String, priority: u8, tags: Vec<String>) {
    let new_id = todos.iter().map(|t| t.id).max().unwrap_or(0) + 1;
    // 先生成 tags 的展示信息
    let tags_info = if tags.is_empty() {
        String::new()
    } else {
        format!("{}", tags.join("/").cyan())
    };
    // 再传递给 Todo::new （tags的所有权在这里就转移出去了）
    let todo = Todo::new(new_id, content, priority, tags);
    let priority_info = if priority > 0 {
        format!(
            "   [{}]",
            match priority {
                2 => "urgent".red().bold().to_string(),
                1 => "high".yellow().to_string(),
                _ => "normal".to_string(),
            }
        )
    } else {
        String::new()
    };
    println!(
        "{} {} Added #{}: {}{}",
        "✔".green(),
        tags_info,
        todo.id,
        todo.content,
        priority_info
    );
    todos.push(todo);
}

fn cmd_list(todos: &[Todo], all: bool, priority: Option<u8>, tag: Option<String>, sort: String) {
    // let items: Vec<&Todo> = if all {
    //     todos.iter().collect()
    // } else {
    //     todos.iter().filter(|t| !t.completed).collect()
    // };
    let mut items: Vec<&Todo> = todos
        .iter()
        .filter(|t| all || !t.completed)
        .filter(|t| match priority {
            Some(p) => t.priority > p,
            None => true,
        })
        .filter(|t| match &tag {
            Some(p) => t.tags.join("").to_string().contains(p),
            None => true,
        })
        .collect();

    match sort.as_str() {
        "priority" => items.sort_by(|a, b| b.priority.cmp(&a.priority)),
        "created" => items.sort_by(|a, b| a.created_at.cmp(&b.created_at)),
        _ => {} // "id": 保持插入排序，什么都不做
    }

    if items.is_empty() {
        println!("Nothing here. Use `tasky add <text>` to create one.");
        return;
    }

    let label = if all { "All" } else { "Pending" };
    print_todos(label, &items);
}

fn cmd_done(todos: &mut Vec<Todo>, id: u32, undo: bool) {
    match todos.iter_mut().find(|t| t.id == id) {
        Some(todo) => {
            let sign = if undo { "Undo" } else { "Done" };
            todo.completed = !undo;
            todo.completed_at = if undo { None } else { Some(Local::now()) };
            println!("{}{} #{}: {}", "✔".green(), sign, id, todo.content);
        }
        None => {
            eprint!("Todo #{} not found.", id);
            std::process::exit(1);
        }
    }
}

fn cmd_edit(todos: &mut Vec<Todo>, id: u32, content: &str) {
    match todos.iter_mut().find(|t| t.id == id) {
        Some(todo) => {
            todo.content = content.to_string();
            println!("{} #{}: {}", "✔ Edit".yellow(), id, content);
        }
        None => {
            eprint!("Todo #{} not found.", id);
            std::process::exit(1);
        }
    }
}

fn cmd_remove(todos: &mut Vec<Todo>, id: u32) {
    let len_before = todos.len();
    todos.retain(|t| t.id != id);
    if todos.len() < len_before {
        println!("Removed #{}", id);
    } else {
        eprintln!("Todo #{} not found.", id);
        std::process::exit(1);
    }
}

fn cmd_search(todos: &[Todo], keyword: &str) {
    // let get_items: Vec<Todo> = todos
    //     .iter()
    //     .filter(|t| t.content.contains(&keyword))
    //     .cloned()
    //     .collect();
    // cmd_list(&get_items, true);
    let matches: Vec<&Todo> = todos
        .iter()
        .filter(|t| t.content.contains(&keyword))
        .collect();
    let label = format!("Search: \"{}\"", keyword);
    print_todos(&label, &matches);
}

fn cmd_clear(todos: &mut Vec<Todo>) {
    let before = todos.len();
    todos.retain(|t| !t.completed);
    let removed = before - todos.len();
    if removed > 0 {
        println!("{} Cleared {} completed todo(s)", "✔".green(), removed);
    } else {
        println!("No completed todos to clear.");
    }
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    let data_dir = cli.data_dir.as_ref(); // Option<&PathBuf>
    let mut todos = load_todos(data_dir)?;

    match cli.command {
        Commands::Add {
            content,
            priority,
            tags,
        } => {
            cmd_add(&mut todos, content, priority, tags);
            save_todos(&todos, data_dir)?;
        }
        Commands::List {
            all,
            priority,
            tag,
            sort,
        } => {
            cmd_list(&todos, all, priority, tag, sort);
        }
        Commands::Done { id, undo } => {
            cmd_done(&mut todos, id, undo);
            save_todos(&todos, data_dir)?;
        }
        Commands::Remove { id } => {
            cmd_remove(&mut todos, id);
            save_todos(&todos, data_dir)?;
        }
        Commands::Search { keyword } => {
            cmd_search(&todos, &keyword);
        }
        Commands::Edit { id, content } => {
            cmd_edit(&mut todos, id, &content);
            save_todos(&todos, data_dir)?;
        }
        Commands::Stats => {
            cmd_stats(&todos);
        }
        Commands::Clear => {
            cmd_clear(&mut todos);
            save_todos(&todos, data_dir)?;
        }
    }

    Ok(())
}
