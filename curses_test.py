#!/usr/bin/env python
# -*- coding: utf-8 -*-
import curses
import time
import locale


locale.setlocale(locale.LC_ALL, '')


# https://docs.python.org/2/library/curses.html
# https://jacobchang.cn/curses-programming-with-python.html
def main(stdscr):
    i = 0
    s = ''
    for per in xrange(0, 101):
        stdscr.addstr(0, 0, '下载A: {}%'.format(per) + ' ' + '=' * 1000, curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(1, 0, '下载A: {}%'.format(per), curses.color_pair(2) | curses.A_UNDERLINE)
        stdscr.addstr(2, 0, '用户输入为: {}'.format(s))
        stdscr.move(3, 0)
        # stdscr.clrtoeol()
        stdscr.refresh()
        time.sleep(1)
        # 输入一个字符
        curses.echo()  # 打开回显
        curses.nocbreak()  # 回车确认
        stdscr.nodelay(False)  # 等待用户输入
        # https://www.thinbug.com/q/16809304
        curses.flushinp()  # 丢弃缓冲区
        s = stdscr.getstr()  # 获取输入字符串
        curses.noecho()  # 关闭回显
        (y, x) = stdscr.getyx()  # 查看y, x
        stdscr.move(y - 1, 0)  # 移动到用户输入的哪一行
        stdscr.clrtoeol()  # 清除用户输入


UP = '\x1b[A'
DOWN = '\x1b[B'
LEFT = '\x1b[D'
RIGHT = '\x1b[C'


def main1(pad):
    i = 0
    s = ''
    line = 0
    col = 0
    for per in xrange(0, 101 * 25):
        pad.addstr(0, 0, '下载: {}%'.format(per) + ' ' + '=' * 900, curses.color_pair(1) | curses.A_BOLD)
        pad.addstr(1, 0, '下载: {}%'.format(per), curses.color_pair(2) | curses.A_UNDERLINE)
        pad.move(2, 0)
        pad.clrtoeol()
        pad.addstr(2, 0, '用户输入为: {}'.format(s))
        pad.move(3, 0)
        pad.clrtoeol()
        pad.addstr(3, 0, '当前坐标: line={}, col={}'.format(line, col))
        pad.move(4, 0)
        # 第一组 line, col 表示显示的pad的左上角
        # 第二组 line, col 窗口的左上角坐标
        # 第三组 line, col 窗口的右下角坐标
        pad.refresh(line, col, 0, 0, curses.LINES - 1, curses.COLS - 1)
        # pad.refresh(0, 0, 4, 1, curses.LINES - 1, curses.COLS - 1)
        time.sleep(0.04)

        # 检测上下左右
        curses.noecho()  # 关闭
        curses.cbreak()  # 不需要回车确认
        pad.nodelay(True)  # 不等待用户输入
        cmd = ''
        while True:
            try:
                cmd += pad.getkey()
            except Exception as e:
                break
        curses.flushinp()
        line = line + cmd.count(DOWN) - cmd.count(UP)
        col = col + (cmd.count(RIGHT) - cmd.count(LEFT)) * 1
        line = 0 if line < 0 else line
        col = 0 if col < 0 else col
        line = 999 if line > 999 else line
        col = 999 if col > 999 else col

        # # 输入一个字符
        # curses.echo()  # 打开回显
        # curses.nocbreak()  # 回车确认
        # pad.nodelay(False)  # 等待用户输入
        # # https://www.thinbug.com/q/16809304
        # curses.flushinp()  # 丢弃缓冲区
        # s = pad.getstr()  # 获取输入字符串
        # curses.noecho()  # 关闭回显
        # (y, x) = pad.getyx()  # 查看y, x
        # pad.move(y - 1, 0)  # 移动到用户输入的哪一行
        # pad.clrtoeol()  # 清除用户输入


if __name__ == "__main__":
    stdscr = curses.initscr()
    pad = curses.newpad(1000, 1000)

    try:
        # 使用颜色首先需要调用这个方法
        curses.start_color()
        # 文字和背景色设置，设置了两个color pair，分别为1和2
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        # 关闭屏幕回显
        curses.noecho()
        # # 输入时不需要回车确认
        # curses.cbreak()
        # 输入时需要回车确认
        curses.nocbreak()
        # 设置nodelay，是否阻塞等待用户输入 False 表示阻塞
        stdscr.nodelay(False)

        line = curses.LINES
        col = curses.COLS

        # main(stdscr)
        main1(pad)
    except Exception, e:
        raise e
    finally:
        # 恢复控制台默认设置（若不恢复，会导致即使程序结束退出了，控制台仍然是没有回显的）
        curses.nocbreak()
        curses.echo()
        # 结束窗口
        curses.endwin()
