from src.Agents.AlphaBetaAgent import AlphaBetaAgent
from src.Agents.humanagent import HumanAgent
from src.Agents.multiastaragent import MultiAStarAgent
from src.Agents.qlearningagent import QLearningAgent
from src.Agents.randomagent import RandomAgent
from src.Agents.minimaxagent import MinimaxAgent
from src.Agents.expectimaxAgent import ExpectimaxAgent
from src.Agents.MCTSAgent import MCTSAgent


class AgentFactory:
    @staticmethod
    def create_agent(agent_type, **kwargs):
        """
        Factory method to create agents based on the type.

        :param agent_type: A string representing the type of agent ('human', 'random', 'minimax', 'qlearning', 'deepqlearning')
        :param kwargs: Additional arguments for specific agents (e.g., depth for Minimax, Q-learning parameters)
        :return: An instance of the selected agent.
        """
        if agent_type.lower() == "human":
            return HumanAgent()
        elif agent_type.lower() == "random":
            return RandomAgent()
        elif agent_type.lower() == "multiastar":
            color = kwargs.get('color', "black")
            depth = kwargs.get('depth', 4)  # Default depth for alphabeta agent is 4
            return MultiAStarAgent(color, depth)
        elif agent_type.lower() == "minimax":
            color = kwargs.get('color', "black")
            depth = kwargs.get('depth', 1)  # Default depth for minimax agent is 1
            return MinimaxAgent(color, depth=depth)
        elif agent_type.lower() == "expectimax":
            color = kwargs.get('color', "black")
            depth = kwargs.get('depth', 2)  # Default depth for expectimax agent is 1
            return ExpectimaxAgent(color, depth=depth)
        elif agent_type.lower() == "alphabeta":
            color = kwargs.get('color', "black")
            depth = kwargs.get('depth', 4)  # Default depth for alphabeta agent is 1
            return AlphaBetaAgent(color, depth=depth)
        elif agent_type.lower() == "qlearning":
            alpha = kwargs.get('alpha', 0.2)
            gamma = kwargs.get('gamma', 0.9)
            epsilon = kwargs.get('epsilon', 0.3)
            initial_q_value = kwargs.get('initial_q_value', 0.1)
            color = kwargs.get('color', "black")
            return QLearningAgent(color, alpha=alpha, gamma=gamma, epsilon=epsilon, initial_q_value=initial_q_value)
        elif agent_type.lower() == "mcts":
            n_simulations = kwargs.get('n_simulations', 100)
            m_steps = kwargs.get('m_steps', 10)
            return MCTSAgent(n_simulations=n_simulations, m_steps=m_steps)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
