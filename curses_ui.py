#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

import curses
import time
import locale
import sys


locale.setlocale(locale.LC_ALL, '')


class MyTerminalUI(object):
    '''终端UI
    * 布局 上方为显示窗口，最后一行为用户输入
    * 命令模式 `:`进入命令模式
    * 默认实现命令 `q` 退出UI
    * 上下左右方向键为滚动条操作
    '''

    # 上下左右的字符
    UP_KEY = '\x1b[A'
    DOWN_KEY = '\x1b[B'
    LEFT_KEY = '\x1b[D'
    RIGHT_KEY = '\x1b[C'
    ENTER_CMD_KEY = ':'

    def _curses_init(self):
        '''初始化curses'''
        curses.initscr()
        # 启用颜色
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        # curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_CYAN)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(9, curses.COLOR_MAGENTA, curses.COLOR_CYAN)
        curses.init_pair(10, curses.COLOR_GREEN, curses.COLOR_CYAN)
        curses.init_pair(11, curses.COLOR_BLUE, curses.COLOR_CYAN)

    def _set_key_mode(self, win):
        # 关闭屏幕回显
        curses.noecho()
        # 输入时不需要回车确认
        curses.cbreak()
        # 隐藏光标
        curses.curs_set(0)
        # 不阻塞立即返回
        win.nodelay(True)

    def _set_input_mode(self, win):
        # 开启屏幕回显
        curses.echo()
        # 输入时需要回车确认
        curses.nocbreak()
        # 显示光标
        curses.curs_set(1)
        # 阻塞等待用户输入
        win.nodelay(False)

    def curses_end(self):
        '''停止curses'''
        # 恢复控制台默认设置（若不恢复，会导致即使程序结束退出了，控制台仍然是没有回显的）
        curses.nocbreak()
        curses.echo()
        # 结束窗口
        curses.endwin()

    def __init__(self, pad_lines=None, pad_cols=None, frame_rate=10):
        '''
        :params:
            pad_lines: 主Pad最大行数 curses.LINES
            pad_cols: 主Pad最大列数 默认为 curses.COLS
            frame_rate: 帧率, 刷新频率
        '''
        self._curses_init()
        self.is_run = False
        self.main_line = 0
        self.main_col = 0
        self.frame = 0
        self.max_lines = curses.LINES
        self.max_cols = curses.COLS
        self.internal_cmd_cb = dict()
        if curses.LINES <= 1:
            self.curses_end()
            raise AttributeError('终端窗口高度不能小于2')
        if curses.COLS <= 10:
            self.curses_end()
            raise AttributeError('终端窗口宽度不能小于10')
        self.pad_lines = pad_lines or self.max_lines
        self.pad_cols = pad_cols or self.max_cols
        self.frame_rate = frame_rate
        # 主窗口
        self.main_win = curses.newpad(self.pad_lines, self.pad_cols)
        # 状态/命令栏
        self.status_cmd_win = curses.newwin(
            1, self.max_cols, self.max_lines - 1, 0)

        # 主窗体默认函数处理函数
        def default_refresh(ui):
            for i in range(0, ui.max_lines - 2):
                ui.exact_update_main(i, 0, 'Main Window', curses.A_BOLD)
            ui.clr_line_status()
            ui.exact_update_status(0, '[Status] frame: {}'.format(
                ui.frame), curses.A_UNDERLINE)

        self.refresh_cb = default_refresh

        def quit_cmd(ui):
            ui.quit()

        self.register_internal_cmd('q', quit_cmd)

    def quit(self):
        self.is_run = False

    def exact_update_main(self, line, col, content, attr=0):
        '''精确更新'''
        self._exact_update(self.main_win, line, col, content, attr)

    def exact_update_status(self, col, content, attr=0):
        '''精确更新'''
        self._exact_update(self.status_cmd_win, 0, col, content, attr)

    def _exact_update(self, win, line, col, content, attr):
        '''精确更新'''
        win.addstr(
            line, col,
            content.encode('utf8') if isinstance(
                content, str) is False else content,
            attr)

    def clr_line_main(self, line):
        self._clr_line(self.main_win, line)

    def clr_line_status(self):
        self._clr_line(self.status_cmd_win, 0)

    def clear_main(self):
        '''清空主窗口'''
        self.main_win.clear()

    def _clr_line(self, win, line):
        '''清空某一行'''
        win.move(line, 0)
        win.clrtoeol()

    def getyx_main(self):
        return self.main_win.getyx()

    def register_internal_cmd(self, cmd, cb):
        self.internal_cmd_cb[cmd] = cb

    def register_refresh(self, cb):
        '''注册刷新函数'''
        self.refresh_cb = cb

    def _scan_key(self):
        self._set_key_mode(self.status_cmd_win)
        cmd = ''
        while True:
            try:
                cmd += self.status_cmd_win.getkey()
            except Exception as e:
                break
        if cmd.count(self.ENTER_CMD_KEY) >= 1:
            return True
        line = self.main_line
        col = self.main_col
        line = line + cmd.count(self.DOWN_KEY) - cmd.count(self.UP_KEY)
        col = col + cmd.count(self.RIGHT_KEY) - cmd.count(self.LEFT_KEY)
        line = 0 if line < 0 else line
        col = 0 if col < 0 else col
        line = self.pad_lines - 1 if line >= self.pad_lines else line
        col = self.pad_cols - 1 if col >= self.pad_cols else col
        self.main_line = line
        self.main_col = col
        return False

    def enter_cmd(self, internal_cmd=True, tips=None, default=None):
        # 清空状态行, 并输出
        self.clr_line_status()
        default_tip = default and "(default:{})".format(default)
        self.exact_update_status(
            0,
            "{}{}: ".format(tips or '', default_tip or ''),
            curses.color_pair(4) | curses.A_DIM)
        self.status_cmd_win.refresh()
        # 等待用户输入
        self._set_input_mode(self.status_cmd_win)
        curses.flushinp()  # 丢弃缓冲区
        user_input = self.status_cmd_win.getstr()  # 获取输入字符串
        if sys.version_info.major == 3:
            user_input = str(user_input, encoding='utf8')
        user_input = str(user_input)
        user_input = user_input.strip()
        self.clr_line_status()
        self.refresh_status()
        if default is not None and (user_input is None or user_input == ""):
            user_input = default
        if internal_cmd:
            if user_input in self.internal_cmd_cb:
                self.internal_cmd_cb[user_input](self)
        # 恢复成key模式
        self._set_key_mode(self.status_cmd_win)
        return user_input

    def refresh_all(self):
        # 将主窗口数据结构刷新到缓冲区
        self.main_win.noutrefresh(
            self.main_line, self.main_col, 0, 0, self.max_lines - 2, self.max_cols - 1)
        # 将状态行数据结构刷新到缓冲区
        self.status_cmd_win.noutrefresh()
        # 执行更新
        curses.doupdate()

    def refresh_status(self):
        self.status_cmd_win.refresh()

    def refresh_main(self):
        self.main_win.refresh(
            self.main_line, self.main_col, 0, 0, self.max_lines - 2, self.max_cols - 1)

    def _run_once(self):
        # 执行窗口刷新函数
        start = time.time()
        self.refresh_cb(self)
        # 渲染
        self.refresh_all()
        # 随眠
        end = time.time()
        delta = end - start
        sleep_sec = 1.0 / self.frame_rate - delta
        if sleep_sec > 0:
            time.sleep(sleep_sec)
        # 检测命令模式
        should_enter_cmd = self._scan_key()
        if should_enter_cmd:
            self.enter_cmd()

        self.frame += 1

    def run(self):
        '''阻塞函数：启动UI'''
        self.is_run = True
        try:
            while self.is_run:
                self._run_once()
        except Exception as e:
            raise e
        finally:
            self.curses_end()


if __name__ == "__main__":
    ui = MyTerminalUI(pad_lines=1000, pad_cols=1000, frame_rate=10)
    ui.run()
