#!/usr/bin/env python3
"""
Test script for Smart Traffic Management System
Run this to verify your installation is working
"""

import sys
import os

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing package imports...")

    packages = [
        'numpy',
        'gymnasium',
        'stable_baselines3',
        'matplotlib',
        'pandas',
        'tensorboard'
    ]

    failed = []
    for package in packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError as e:
            print(f"  ✗ {package}: {e}")
            failed.append(package)

    # Test SUMO-RL
    try:
        import sumo_rl
        print(f"  ✓ sumo-rl")
    except ImportError:
        print(f"  ⚠ sumo-rl (optional)")

    # Test TraCI
    try:
        import traci
        print(f"  ✓ traci")
    except ImportError:
        print(f"  ⚠ traci (needed for SUMO)")

    return len(failed) == 0

def test_sumo():
    """Test SUMO configuration"""
    print("\nTesting SUMO configuration...")

    if 'SUMO_HOME' in os.environ:
        print(f"  ✓ SUMO_HOME = {os.environ['SUMO_HOME']}")
        return True
    else:
        print("  ✗ SUMO_HOME not set")
        return False

def test_rl_environment():
    """Test creating a simple RL environment"""
    print("\nTesting RL environment creation...")

    try:
        import gymnasium as gym
        from stable_baselines3 import PPO

        # Create a simple environment
        env = gym.make('CartPole-v1')
        print("  ✓ Gymnasium environment created")

        # Create a PPO model
        model = PPO('MlpPolicy', env, verbose=0)
        print("  ✓ PPO model created")

        env.close()
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("Smart Traffic Management System - Installation Test")
    print("="*50)

    results = []
    results.append(test_imports())
    results.append(test_sumo())
    results.append(test_rl_environment())

    print("\n" + "="*50)
    if all(results):
        print("✅ All tests passed! Your system is ready.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("="*50)
