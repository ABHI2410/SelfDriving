from stable_baselines3 import PPO #PPO
from typing import Callable
import os
from RL.environment import Env
import time

class Model():
    def __init__(self,sce) -> None:
        self.sce = sce
        self.model_dir = f"models/{int(time.time())}"
        self.log_dir = f"logs/{int(time.time())}"
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def train(self):
        env = Env(self.sce)
        obs = env.reset()
        model = PPO('MlpPolicy',env,verbose=1,learning_rate= 0.01,tensorboard_log=self.log_dir)
        TIMESTEPS = 500_000
        iter = 0
        print("Starting Training ")
        done = False
        while iter <1:
            iter +=1 
            env.reset()
            while not done:
                action, _states = model.predict(obs)
                obs, reward, done, info = env.step(action)
                # Check if the environment needs to be reset
                if done:
                    env.rest()
            model.save(f"{self.models_dir}/{TIMESTEPS*iter}")
    
    def test(self,model_path):
        env = Env()
        obs = env.reset()
        model = PPO.load(model_path,env=env)
        episodes = 5

        for ep in range(episodes):
            obs = env.reset()
            done = False
            while not done:
                action, _states = model.predict(obs)
                obs, reward, done, info = env.step(action)
                #env.render()
                print(reward)