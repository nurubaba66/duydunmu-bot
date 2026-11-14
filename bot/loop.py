"""Sürekli çalışma: her LOOP_MINUTES dakikada bir tur atar, durumu kaydeder; süre dolunca kendini yeniden başlatır."""
import subprocess
import time
import traceback

import requests

from . import config, main

GIT = ["git", "-c", "user.name=duydunmu-bot", "-c", "user.email=bot@users.noreply.github.com"]


def sh(*args):
    return subprocess.run(list(args), capture_output=True, text=True)


def sync_in():
    sh("git", "pull", "--rebase", "-q", "-X", "theirs")


def sync_out(msg="durum güncellendi"):
    sh("git", "add", "state/state.json", "pending")
    if sh("git", "diff", "--cached", "--quiet").returncode != 0:
        sh(*GIT, "commit", "-q", "-m", msg)
        for _ in range(3):
            sh("git", "pull", "--rebase", "-q", "-X", "ours")
            if sh("git", "push", "-q").returncode == 0:
                break
            time.sleep(5)


def restart():
    r = requests.post(f"https://api.github.com/repos/{config.GITHUB_REPO}/actions/workflows/loop.yml/dispatches",
                      headers={"Authorization": f"Bearer {config.GITHUB_TOKEN}", "Accept": "application/vnd.github+json"},
                      json={"ref": "main"}, timeout=30)
    print("Yeniden başlatma:", r.status_code)


def run():
    start = time.time()
    while time.time() - start < config.LOOP_MAX_MINUTES * 60:
        t0 = time.time()
        sync_in()
        try:
            main.main()
        except Exception:
            traceback.print_exc()
        sync_out()
        wait = config.LOOP_MINUTES * 60 - (time.time() - t0)
        if wait > 0:
            time.sleep(wait)
    restart()


if __name__ == "__main__":
    run()
