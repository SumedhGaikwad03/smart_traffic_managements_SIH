"""
train_agent.py - Train DQN Agent on SUMO Traffic Environment

Deep Q-Network (DQN) implementation for traffic signal control
using real SUMO simulation with actual network and route files.

Usage:
    python train_agent.py
"""

import numpy as np
import random
from collections import deque
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

from env_sumo_rl import SumoTrafficEnv


class DQN(nn.Module):
    """
    Deep Q-Network for traffic signal control
    
    Simple 3-layer MLP that maps state to Q-values for each action
    """
    
    def __init__(self, state_dim, action_dim, hidden_dim=64):
        """
        Initialize DQN
        
        Args:
            state_dim: Dimension of state space
            action_dim: Number of possible actions
            hidden_dim: Hidden layer size
        """
        super(DQN, self).__init__()
        
        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, action_dim)
    
    def forward(self, x):
        """
        Forward pass
        
        Args:
            x: State tensor
        
        Returns:
            Q-values for each action
        """
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)


class ReplayBuffer:
    """
    Experience replay buffer for DQN
    
    Stores transitions and samples random batches for training
    """
    
    def __init__(self, capacity=10000):
        """
        Initialize replay buffer
        
        Args:
            capacity: Maximum number of transitions to store
        """
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        """Add transition to buffer"""
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size):
        """Sample random batch of transitions"""
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return (np.array(states), np.array(actions), np.array(rewards),
                np.array(next_states), np.array(dones))
    
    def __len__(self):
        """Return current buffer size"""
        return len(self.buffer)


class DQNAgent:
    """
    DQN Agent for traffic signal control
    
    Uses experience replay and target network for stable training
    """
    
    def __init__(self, state_dim, action_dim, learning_rate=0.001,
                 gamma=0.95, epsilon=1.0, epsilon_decay=0.995,
                 epsilon_min=0.01, buffer_size=10000, batch_size=64):
        """
        Initialize DQN agent
        
        Args:
            state_dim: State space dimension
            action_dim: Action space dimension
            learning_rate: Learning rate for optimizer
            gamma: Discount factor
            epsilon: Initial exploration rate
            epsilon_decay: Epsilon decay rate per episode
            epsilon_min: Minimum epsilon value
            buffer_size: Replay buffer capacity
            batch_size: Training batch size
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        
        # Device (CPU or GPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Q-network and target network
        self.q_network = DQN(state_dim, action_dim).to(self.device)
        self.target_network = DQN(state_dim, action_dim).to(self.device)
        self.target_network.load_state_dict(self.q_network.state_dict())
        
        # Optimizer
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        
        # Replay buffer
        self.replay_buffer = ReplayBuffer(buffer_size)
        
        # Training metrics
        self.loss_history = []
    
    def get_action(self, state, training=True):
        """
        Select action using epsilon-greedy policy
        
        Args:
            state: Current state
            training: If True, use epsilon-greedy; else greedy
        
        Returns:
            action: Selected action
        """
        if training and random.random() < self.epsilon:
            # Explore: random action
            return random.randint(0, self.action_dim - 1)
        else:
            # Exploit: best action from Q-network
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            with torch.no_grad():
                q_values = self.q_network(state_tensor)
            return q_values.argmax().item()
    
    def store_transition(self, state, action, reward, next_state, done):
        """Store transition in replay buffer"""
        self.replay_buffer.push(state, action, reward, next_state, done)
    
    def train(self):
        """
        Train Q-network on batch from replay buffer
        
        Returns:
            loss: Training loss (None if buffer too small)
        """
        if len(self.replay_buffer) < self.batch_size:
            return None
        
        # Sample batch
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(
            self.batch_size)
        
        # Convert to tensors
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)
        
        # Current Q-values
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        
        # Target Q-values (using target network)
        with torch.no_grad():
            max_next_q_values = self.target_network(next_states).max(1)[0]
            target_q_values = rewards + (1 - dones) * self.gamma * max_next_q_values
        
        # Compute loss
        loss = F.mse_loss(current_q_values.squeeze(), target_q_values)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        self.loss_history.append(loss.item())
        return loss.item()
    
    def update_target_network(self):
        """Copy Q-network weights to target network"""
        self.target_network.load_state_dict(self.q_network.state_dict())
    
    def decay_epsilon(self):
        """Decay exploration rate"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def save(self, filepath):
        """Save model weights"""
        torch.save({
            'q_network': self.q_network.state_dict(),
            'target_network': self.target_network.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'epsilon': self.epsilon
        }, filepath)
        print(f"Model saved to {filepath}")
    
    def load(self, filepath):
        """Load model weights"""
        checkpoint = torch.load(filepath)
        self.q_network.load_state_dict(checkpoint['q_network'])
        self.target_network.load_state_dict(checkpoint['target_network'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        self.epsilon = checkpoint['epsilon']
        print(f"Model loaded from {filepath}")


def train_dqn(env, agent, n_episodes=100, target_update_freq=10, print_every=10):
    """
    Train DQN agent on SUMO environment
    
    Args:
        env: SumoTrafficEnv instance
        agent: DQNAgent instance
        n_episodes: Number of training episodes
        target_update_freq: Update target network every N episodes
        print_every: Print statistics every N episodes
    
    Returns:
        episode_rewards: List of total rewards per episode
        episode_stats: List of statistics per episode
    """
    episode_rewards = []
    episode_stats = []
    
    print("\n" + "="*70)
    print("Starting DQN Training on SUMO Environment")
    print(f"Training for {n_episodes} episodes")
    print("="*70 + "\n")
    
    for episode in range(n_episodes):
        state = env.reset()
        episode_reward = 0
        done = False
        step_count = 0
        
        while not done:
            # Select action
            action = agent.get_action(state, training=True)
            
            # Take action in environment
            next_state, reward, done, info = env.step(action)
            
            # Store transition
            agent.store_transition(state, action, reward, next_state, done)
            
            # Train agent
            loss = agent.train()
            
            # Update state and metrics
            state = next_state
            episode_reward += reward
            step_count += 1
        
        # Decay epsilon
        agent.decay_epsilon()
        
        # Update target network periodically
        if (episode + 1) % target_update_freq == 0:
            agent.update_target_network()
        
        # Store episode statistics
        episode_rewards.append(episode_reward)
        episode_stats.append(info)
        
        # Print progress
        if (episode + 1) % print_every == 0:
            avg_reward = np.mean(episode_rewards[-print_every:])
            avg_queue = np.mean([s['total_queue'] for s in episode_stats[-print_every:]])
            avg_waiting = np.mean([s['total_waiting'] for s in episode_stats[-print_every:]])
            recent_loss = np.mean(agent.loss_history[-100:]) if agent.loss_history else 0
            
            print(f"Episode {episode + 1}/{n_episodes}")
            print(f"  Avg Reward: {avg_reward:.2f}")
            print(f"  Avg Total Queue: {avg_queue:.2f}")
            print(f"  Avg Total Waiting Time: {avg_waiting:.2f}")
            print(f"  Epsilon: {agent.epsilon:.3f}")
            print(f"  Loss: {recent_loss:.4f}")
            print(f"  Buffer Size: {len(agent.replay_buffer)}\n")
    
    print("="*70)
    print("Training Complete!")
    print("="*70 + "\n")
    
    return episode_rewards, episode_stats


def evaluate_agent(env, agent, n_episodes=10, render=False):
    """
    Evaluate trained agent
    
    Args:
        env: SumoTrafficEnv instance
        agent: Trained DQNAgent
        n_episodes: Number of evaluation episodes
        render: Whether to print states
    
    Returns:
        avg_reward: Average reward
        avg_queue: Average total queue length
        avg_waiting: Average total waiting time
    """
    total_rewards = []
    total_queues = []
    total_waiting_times = []
    
    print(f"Evaluating trained agent over {n_episodes} episodes...\n")
    
    for episode in range(n_episodes):
        state = env.reset()
        episode_reward = 0
        done = False
        
        if render and episode == 0:
            print(f"\n{'='*50}")
            print(f"Sample Evaluation Episode")
            print(f"{'='*50}")
        
        while not done:
            # Use greedy policy (no exploration)
            action = agent.get_action(state, training=False)
            
            if render and episode == 0:
                env.render()
            
            next_state, reward, done, info = env.step(action)
            
            state = next_state
            episode_reward += reward
        
        total_rewards.append(episode_reward)
        total_queues.append(info['total_queue'])
        total_waiting_times.append(info['total_waiting'])
    
    avg_reward = np.mean(total_rewards)
    avg_queue = np.mean(total_queues)
    avg_waiting = np.mean(total_waiting_times)
    
    print(f"\n{'='*70}")
    print("Evaluation Results (RL Agent):")
    print(f"{'='*70}")
    print(f"Average Reward: {avg_reward:.2f}")
    print(f"Average Total Queue Length: {avg_queue:.2f}")
    print(f"Average Total Waiting Time: {avg_waiting:.2f}")
    
    return avg_reward, avg_queue, avg_waiting


def evaluate_fixed_time_baseline(env, n_episodes=10, cycle_length=20):
    """
    Evaluate fixed-time control baseline
    
    Args:
        env: SumoTrafficEnv instance
        n_episodes: Number of evaluation episodes
        cycle_length: Steps per phase
    
    Returns:
        avg_reward: Average reward
        avg_queue: Average total queue
        avg_waiting: Average total waiting time
    """
    total_rewards = []
    total_queues = []
    total_waiting_times = []
    
    print(f"\nEvaluating fixed-time baseline over {n_episodes} episodes...\n")
    
    for episode in range(n_episodes):
        state = env.reset()
        episode_reward = 0
        done = False
        step_count = 0
        
        while not done:
            # Fixed-time control: alternate every cycle_length steps
            action = 0 if (step_count // cycle_length) % 2 == 0 else 1
            
            next_state, reward, done, info = env.step(action)
            
            episode_reward += reward
            step_count += 1
        
        total_rewards.append(episode_reward)
        total_queues.append(info['total_queue'])
        total_waiting_times.append(info['total_waiting'])
    
    avg_reward = np.mean(total_rewards)
    avg_queue = np.mean(total_queues)
    avg_waiting = np.mean(total_waiting_times)
    
    print(f"\n{'='*70}")
    print("Evaluation Results (Fixed-Time Baseline):")
    print(f"{'='*70}")
    print(f"Average Reward: {avg_reward:.2f}")
    print(f"Average Total Queue Length: {avg_queue:.2f}")
    print(f"Average Total Waiting Time: {avg_waiting:.2f}")
    
    return avg_reward, avg_queue, avg_waiting


def main():
    """Main training and evaluation pipeline"""
    print("\n" + "="*70)
    print("SUMO-Based Reinforcement Learning for Traffic Signal Control")
    print("SIH25050: Smart Traffic Management System")
    print("="*70 + "\n")
    
    # Set random seeds
    np.random.seed(42)
    random.seed(42)
    torch.manual_seed(42)
    
    # Configuration
    CONFIG_FILE = "/../sumo_network/myconfig.sumocfg"
    USE_GUI = True  # Set to True to visualize SUMO during training
    MAX_STEPS = 1000  # Steps per episode
    N_EPISODES = 100  # Training episodes
    
    # Initialize environment
    print("Initializing SUMO environment...")
    env = SumoTrafficEnv(
        config_file=CONFIG_FILE,
        max_steps=MAX_STEPS,
        gui=USE_GUI,
        delta_time=5  # RL decision every 5 simulation steps
    )
    
    # Initialize DQN agent
    print("Initializing DQN agent...\n")
    agent = DQNAgent(
        state_dim=env.n_states,
        action_dim=env.n_actions,
        learning_rate=0.001,
        gamma=0.95,
        epsilon=1.0,
        epsilon_decay=0.995,
        epsilon_min=0.01,
        buffer_size=10000,
        batch_size=64
    )
    
    # Train agent
    try:
        episode_rewards, episode_stats = train_dqn(
            env, agent,
            n_episodes=N_EPISODES,
            target_update_freq=10,
            print_every=10
        )
        
        # Save trained model
        agent.save("traffic_dqn_model.pth")
        
        # Evaluate trained agent
        print("\n" + "="*70)
        print("PERFORMANCE COMPARISON")
        print("="*70 + "\n")
        
        rl_reward, rl_queue, rl_waiting = evaluate_agent(
            env, agent, n_episodes=20, render=False
        )
        
        baseline_reward, baseline_queue, baseline_waiting = evaluate_fixed_time_baseline(
            env, n_episodes=20, cycle_length=20
        )
        
        # Compare performance
        print(f"\n{'='*70}")
        print("IMPROVEMENT OVER BASELINE:")
        print(f"{'='*70}")
        queue_improvement = ((baseline_queue - rl_queue) / baseline_queue) * 100
        waiting_improvement = ((baseline_waiting - rl_waiting) / baseline_waiting) * 100
        print(f"Queue Length Reduction: {queue_improvement:.2f}%")
        print(f"Waiting Time Reduction: {waiting_improvement:.2f}%")
        print(f"{'='*70}\n")
        
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user.")
    
    except Exception as e:
        print(f"\n\nError during training: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Always close environment
        env.close()
        print("\nSUMO environment closed.")
    
    print("\n" + "="*70)
    print("Training and Evaluation Complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()