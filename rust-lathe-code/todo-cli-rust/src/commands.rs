use crate::todo::Todo;
use colored::Colorize;

pub fn cmd_stats(todos: &[Todo]) {
    if todos.is_empty() {
        print!("Nothing here");
        return;
    }
    // 任务总数
    let total_count = todos.len();
    // 完成的任务数
    let finished_todos: Vec<&Todo> = todos.iter().filter(|t| t.completed).collect();
    // 各个优先级数量
    let mut level_zero = 0;
    let mut level_one = 0;
    let mut level_two = 0;
    for t in todos {
        match t.priority {
            0 => level_zero += 1,
            1 => level_one += 1,
            2 => level_two += 1,
            _ => {}
        }
    }
    println!(
        "待办总数为：{}，已经完成的任务数为：{}, 未完成数量：{}",
        total_count,
        finished_todos.len(),
        total_count - finished_todos.len(),
    );
    println!(
        "各个优先级待办数量：{}:{} {}:{} {}:{}",
        "普通待办",
        level_zero,
        "高等级待办".yellow(),
        level_one.to_string().yellow(),
        "紧急待办".red().bold(),
        level_two.to_string().red().bold()
    )
}
