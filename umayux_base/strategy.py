import time
import sys
import getopt

from parser import parse
from state import WorldState
from communication import ReceiveDataThread, SendActionsThread, UpdateTicThread


class StrategyBase(object):
    ws = WorldState()
    x = -1.0
    y = 0.0

    def get_initial_position(self, kick_off_side="l"):
        return self.x, self.y

    def move_to_initial_position(self, kick_off_side="l"):
        x, y = self.get_initial_position(kick_off_side)
        print self.ws.side, x, y
        self.ws.send("(move %f %f)" % (x, y))

    def select_team_name(self):
        opts, args = getopt.getopt(sys.argv[1:],"ht:",["help", "team="])
        for opt, arg in opts:
            if opt in ("-t", "--team"):
                self.ws.team_name = arg
            elif opt in ("-h", "--help"):
                print "Usage: ./%s -t TeamName" % sys.argv[0]
                sys.exit(0)

    def init(self):
        self.select_team_name()

        self.ws.send("(init %s)" % self.ws.team_name)
        msg =  parse(self.ws.recv())
        self.ws.side = msg[1]
        self.ws.unum = msg[2]
        self.ws.play_mode = msg[3]
        print "Side:", self.ws.side, ", Unum:", self.ws.unum

        self.move_to_initial_position(kick_off_side="l")

    def play_on(self):
        self.ws.do = "(turn 50)"

    def kick_in(self):
        self.move_to_initial_position()

    def kick_off(self, side="l"):
        if self.ws.side == side:
            self.ws.do = "(kick 10 90)"

    def goal(self):
        self.move_to_initial_position()

    def goal_kick(self):
        self.move_to_initial_position()

    def run(self):
        # INIT
        self.init()

        # INIT THREADS
        receive_data_thread = ReceiveDataThread()
        receive_data_thread.daemon = True
        receive_data_thread.start()
        send_actions_thread = SendActionsThread()
        send_actions_thread.daemon = True
        send_actions_thread.start()
        update_tic_thread = UpdateTicThread()
        update_tic_thread.daemon = True
        update_tic_thread.start()

        # STRATEGY
        while True:
            if self.ws.play_mode == "play_on":
                self.play_on()
            elif self.ws.play_mode == "kick_off_" + self.ws.side:
                self.kick_off()
            elif self.ws.play_mode.startswith("goal"):
                self.goal()
            time.sleep(0.05)