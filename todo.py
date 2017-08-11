from datetime import date,time
import redis
import os
import sys
import hashlib
import types
try:
    import argparse
except Exception as e:
    print("argparse module missing: Please run 'sudo easy_install argparse'")
    sys.exit(1)

r = redis.StrictRedis(host='192.168.0.108', port=6379, db=0)
class myTODO():

    @staticmethod
    def __hash(text):
        hash=hashlib.md5()
        hash.update(text.encode('utf-8'))
        return hash.hexdigest()

    def add_task(self, task_text, time_to_finish):
        task_id = self.__hash(task_text)
        task_text = str(task_text)
        time_to_finish = str(time_to_finish)
        time_list = time_to_finish.split(' ')
        finish_time = ""
        for time in time_list:
            finish_time += '-' + time
        r.sadd('undo', task_id)
        hmDict = {"task_name": task_text, "deadline": time_to_finish}
        r.hmset(task_id,hmDict)

    def finish_task(self, task_text):
        task_id = self.__hash(task_text)
        r.srem('undo',task_id)
        r.sadd('finish',task_id)
    
    def del_task(self, task_text):
        task_id = self.__hash(task_text)
        r.srem('undo',task_id)
        r.sadd('del',task_id)

    def update_task(self, task_text, time_to_finish):
        task_id = self.__hash(task_text)
        if r.sismember('undo', task_id):
            r.hset(task_id, "deadline", time_to_finish)
        else:
            print("没有该任务或者已被删除、完成")
            sys.exit(1)

    def show_undo(self):
        undo_blist = r.smembers('undo')
        undo_list=[undo_term.decode('ascii') for undo_term in undo_blist]
        for undo in undo_list:
            the_task = r.hmget(undo,["task_name","deadline"])
            str_task = bytes.decode(the_task[1]) + ":" + bytes.decode(the_task[0])
            print("[UNDO]"+str_task)

    def show_finish(self):
        finish_blist = r.smembers('finish')
        finish_list=[finish_term.decode('ascii') for finish_term in finish_blist]
        for finish in finish_list:
            the_task = r.hmget(finish, ["task_name","deadline"])
            # str_task = ""
            str_task =bytes.decode(the_task[1]) + ":" + bytes.decode(the_task[0])
            print("[DONE]" + str_task)
        # print('\n')

    def show_del(self):
        del_blist = r.smembers('del')
        del_list=[del_term.decode('ascii') for del_term in del_blist]
        for del_ in del_list:
            the_task = r.hmget(del_, ["task_name","deadline"])
            # str_task = ""
            str_task = bytes.decode(the_task[1]) + ":" + bytes.decode(the_task[0])
            print("[DELE]"+str_task)
        # print('\n')

    def show_all(self):
        print("-----------------------------------")
        print("here is all the done/undo tasks.")
        print("-----------------------------------")
        self.show_undo()
        print("-----------------------------------")
        self.show_finish()
        print("-----------------------------------")
        # self.show_del()
        
        
        



def get_args():
    usage = '%(prog)s [options] [TEXT]'
    parser = argparse.ArgumentParser(description='Command-line todo - t Help',
            usage = usage)

    action_group = parser.add_argument_group("Action")
    action_group.add_argument('-a','--add', dest='add', nargs='+', help='add a task')
    action_group.add_argument('-u','--update', dest='update', nargs='+', help=
            'update a task in aspect of time-to-finish field')
    action_group.add_argument('-f','--finish', dest='finish', nargs='+', help = 'finish a task')
    action_group.add_argument('-d','--del', dest='delete', nargs='+', help = 'delete a task')

    output_group = parser.add_argument_group('Show')
    output_group.add_argument('--done', dest='done', action='store_true', 
            help='List all the done tasks')
    output_group.add_argument('--undo', dest='undo', action='store_true', 
            help='List all the undo tasks')
    output_group.add_argument('--deleted', dest='deleted', action='store_true', 
            help='List all the deleted tasks')    
    output_group.add_argument('--all', dest='all', action='store_true', 
            help='List all done/undo tasks')    

    args = parser.parse_args()
    return args

def main():
    args = get_args()
    t = myTODO()

    try:
        if args.done:
            t.show_finish()
        elif args.deleted:
            t.show_del()
        elif args.undo:
            t.show_undo()
        elif args.add:
            t.add_task(args.add[0],args.add[1])
            t.show_undo()
        elif args.delete:
            t.del_task(args.delete[0])
            t.show_del()
        elif args.finish:
            t.finish_task(args.finish[0])
            t.show_finish()
        elif args.update:
            t.update_task(args.update[0],args.update[1])
            t.show_undo()
        elif args.all:
            t.show_all()
    except Exception as e:
        print(">>ERROR:",str(e))        
        sys.exit(1)

if __name__ == '__main__':
    main()
