



def compute_loss(batch, policy_net, target_net, gamma):
    states, actions, rewards, next_states, dones = batch

    state_batch = torch.FloatTensor(states)
    action_batch = torch.LongTensor(actions).unsqueeze(1)
    reward_batch = torch.FloatTensor(rewards)
    next_state_batch = torch.FloatTensor(next_states)
    done_batch = torch.BoolTensor(dones)

    # Compute Q-values for the current states
    current_q_values = policy_net(state_batch).gather(1, action_batch)

    # Compute the target Q-values
    next_q_values = target_net(next_state_batch).max(1)[0].detach()
    target_q_values = reward_batch + (gamma * next_q_values * (1 - done_batch))

    # Compute loss
    loss = nn.functional.mse_loss(current_q_values, target_q_values.unsqueeze(1))

    return loss



# Hyperparameters
batch_size = 128
gamma = 0.99  # Discount factor
epsilon_start = 1.0
epsilon_end = 0.01
epsilon_decay = 500
target_update = 10  # Update target network every 10 episodes

# Initialize networks and optimizer
policy_net = QNetwork(state_dim, action_dim)
target_net = QNetwork(state_dim, action_dim)
target_net.load_state_dict(policy_net.state_dict())
target_net.eval()  # Set target network to evaluation mode
optimizer = optim.Adam(policy_net.parameters(), lr=lr)

# Initialize replay buffer
replay_buffer = ReplayBuffer(10000)

# Exploration rate
epsilon = epsilon_start

# Training loop
for episode in range(num_episodes):
    state = env.reset()
    total_reward = 0

    for t in range(max_timesteps):
        # Select action with epsilon-greedy policy
        if random.random() > epsilon:
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state).unsqueeze(0)
                action = policy_net(state_tensor).max(1)[1].item()
        else:
            action = random.randrange(action_dim)

        # Step the environment
        next_state, reward, done = env.step(action)
        total_reward += reward

        # Store the transition in the replay buffer
        replay_buffer.push(state, action, reward, next_state, done)

        # Update the state
        state = next_state

        # Perform one step of optimization
        if len(replay_buffer) > batch_size:
            transitions = replay_buffer.sample(batch_size)
            batch = Transition(*zip(*transitions))

            # Compute loss and optimize the policy network
            loss = compute_loss(batch, policy_net, target_net, gamma)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        if done:
            break

    # Update epsilon
    epsilon = max(epsilon_end, epsilon - (epsilon_start - epsilon_end) / epsilon_decay)

    # Update the target network
    if episode % target_update == 0:
        target_net.load_state_dict(policy_net.state_dict())

    print(f"Episode {episode + 1}: Total Reward = {total_reward}")

# Close the environment
env.close()

