use assert_cmd::Command;
use predicates::prelude::*;
use tempfile::TempDir;

fn setup_data_dir() -> TempDir {
    tempfile::tempdir().unwrap()
}

#[test]
fn test_add_and_list() {
    let tmp = setup_data_dir();
    let dir = tmp.path().to_str().unwrap();

    // 添加一条待办
    Command::cargo_bin("tasky")
        .unwrap()
        .args(&["--data-dir", dir, "add", "测试任务"])
        .assert()
        .success()
        .stdout(predicate::str::contains("Added #1"));

    // 列出待办
    Command::cargo_bin("tasky")
        .unwrap()
        .args(&["--data-dir", dir, "list"])
        .assert()
        .success()
        .stdout(predicate::str::contains("测试任务"));
}

#[test]
fn test_done_marks_completed() {
    let tmp = setup_data_dir();
    let dir = tmp.path().to_str().unwrap();

    // 先添加
    Command::cargo_bin("tasky")
        .unwrap()
        .args(&["--data-dir", dir, "add", "完成任务"])
        .assert()
        .success();

    // 标记完成
    Command::cargo_bin("tasky")
        .unwrap()
        .args(&["--data-dir", dir, "done", "1"])
        .assert()
        .success()
        .stdout(predicate::str::contains("Done #1"));

    // 默认 list 不应显示已完成的
    Command::cargo_bin("tasky")
        .unwrap()
        .args(&["--data-dir", dir, "list"])
        .assert()
        .success()
        .stdout(predicate::str::contains("Nothing here"));
}

#[test]
fn test_remove_nonexistent() {
    let tmp = setup_data_dir();
    let dir = tmp.path().to_str().unwrap();

    Command::cargo_bin("tasky")
        .unwrap()
        .args(&["--data-dir", dir, "remove", "99"])
        .assert()
        .failure();
}

#[test]
fn test_clear_removes_completed() {
    let tmp = setup_data_dir();
    let dir = tmp.path().to_str().unwrap();

    Command::cargo_bin("tasky")
        .unwrap()
        .args(&["--data-dir", dir, "add", "将被清理"])
        .assert()
        .success();

    Command::cargo_bin("tasky")
        .unwrap()
        .args(&["--data-dir", dir, "done", "1"])
        .assert()
        .success();

    Command::cargo_bin("tasky")
        .unwrap()
        .args(&["--data-dir", dir, "clear"])
        .assert()
        .success()
        .stdout(predicate::str::contains("Cleared 1"));

    Command::cargo_bin("tasky")
        .unwrap()
        .args(&["--data-dir", dir, "list", "--all"])
        .assert()
        .success()
        .stdout(predicate::str::contains("Nothing here"));
}
