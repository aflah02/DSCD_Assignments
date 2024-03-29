import subprocess
import argparse

def run_and_log(node_id):
    log_file = f"node_{node_id}.log"
    print(f"Logging to {log_file}")
    with open(log_file, 'w') as log:
        process = subprocess.Popen([f'python RAFT_Node.py --nodeId {node_id}'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        for line in process.stdout:
            log.write(line)
            print(line, end='')  # Optional: print to console as well
            
        process.wait()

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--nodeId", type=int, required=True)
    args = argparser.parse_args()
    node_id = args.nodeId
    run_and_log(node_id)
