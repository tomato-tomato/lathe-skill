use clap::{Parser, Subcommand};
use std::path::PathBuf;

#[derive(Parser)]
#[command(name = "tasky", version, about = "A tiny todo manager")]
pub struct Cli {
    /// Custom data directory(overrides default)
    #[arg(long, global = true)]
    pub data_dir: Option<PathBuf>,
    #[command(subcommand)]
    pub command: Commands,
}

#[derive(Subcommand)]
pub enum Commands {
    /// Add a new todo
    Add {
        /// The task description
        #[arg(required = true)]
        content: String,
        // The priority of the task (0: 普通, 1:高, 2:紧急)
        #[arg(short, long, default_value_t = 0)]
        priority: u8,
        // The tags of the task
        #[arg(short, long)]
        tags: Vec<String>,
    },
    /// Edit a todo
    Edit {
        /// the Id of the todo
        #[arg(required = true)]
        id: u32,
        /// the changed content
        #[arg(required = true)]
        content: String,
    },
    /// List todos(pending by default)
    List {
        /// show all todos including completed
        #[arg(short, long)]
        all: bool,
        /// show above the level's priority
        #[arg(short, long)]
        priority: Option<u8>,
        /// show contain the tag's toso
        #[arg(short, long)]
        tag: Option<String>,
        /// sort order：id, priority, created
        #[arg(short, long, default_value = "id")]
        sort: String,
    },
    /// Mark a todo as done
    Done {
        /// the Id of the todo to complete
        id: u32,
        /// undo the task
        #[arg(long)]
        undo: bool,
    },
    /// Remove a todo
    Remove {
        /// The ID of the todo to remove
        id: u32,
    },
    /// Search the task include content
    Search {
        /// The content for search
        keyword: String,
    },
    /// show statistics
    Stats,
    /// Remove all completed todos
    Clear,
}
