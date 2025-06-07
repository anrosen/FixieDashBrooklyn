# 🚴‍♂️ FixieDashBrooklyn

A challenging cycling timing game where you master the art of pedaling rhythm on your fixed-gear bike! Test your precision and timing as you navigate through multiple levels, hitting the perfect pedal zones to maintain speed and avoid falling.

## 🎮 Game Features

- **Precision Timing Gameplay**: Hit the green timing zones to maintain speed and stamina energy
- **Multi-Level Challenge**: Progress through 4 challenging levels with increasing distances
- **Physics-Based Mechanics**: Realistic speed, stamina fatigue, and momentum systems
- **User Management**: Sign in to track your progress and compete on leaderboards
- **Comprehensive Stats Tracking**: Monitor your performance - race to get the furthest the fastest
- **Modern UI**: Clean, responsive interface with real-time feedback
- **Background Animations**: Dynamic backgrounds that change as you progress

## 🛠️ Tech Stack

### Client (Game Engine)

- **Python 3.8+** with Pygame for game rendering and input handling
- **Dependency Injection Container** for clean service management
- **Modular Architecture** with separate services for game logic, API communication, and background events
- **Configuration Management** with JSON-based settings

### Server (Backend API)

- **Node.js 18+** with TypeScript for type safety
- **Express.js** REST API with comprehensive error handling
- **Dependency Injection** using TSyringe
- **In-Memory Data Storage** for sessions, users, and game results

## 📋 Prerequisites

- **Python 3.8 or higher**
- **Node.js 18.0 or higher**
- **npm** (comes with Node.js)
- **Git** (for cloning the repository)

## 🚀 Quick Start

### Automated Setup

1. **Clone the Repository**

```bash
git clone <your-repo-url>
cd FixieDashBrooklyn
```

2. **Set Up Client with Auto-Setup Script**

```bash
cd client
python setup_dev.py
```

This script will:

- Check Python version compatibility (I am on 3.10.15)
- Create and activate virtual environment
- Install all dependencies
- Verify assets are present
- Show next steps

3. **Set Up Server**

```bash
cd ../server
npm install
npm run build
```

## 🎯 Running the Game

### Multiplayer Mode (With Leaderboards)

1. **Start the Server:**

```bash
cd server
npm run dev  # Development with hot reload
# OR
npm start    # Production mode
```

Server runs on `http://localhost:3000`

2. **Start the Client:**

```bash
cd client
source venv/bin/activate
python main.py
```

### Single Player Mode

```bash
cd client
# Make sure virtual environment is activated
source venv/bin/activate  # On macOS/Linux
python main.py
```

## 🎮 How to Play

### Game Mechanics

- **Timing Line**: A white line moves horizontally across the pedal zone
- **Green Zone**: The sweet spot - hit this area for perfect pedaling efficiency and regain stamina
- **Stamina System**: When your timing is not at your efficient cadence, stamina decreases
- **Speed Control**: By pedaling sooner than your efficient cadence, you speed up - by pedaling later, you slow down
- **Falling Mechanic**: Run out of stamina and you'll crash, which ends the game
- **Distance Goal**: Each level has a target distance to complete

### Controls

- **Left/Right Arrow Keys**: Pedal when the timing line enters the green zone
- **ESC**: Pause/unpause the game
- **F11**: Toggle fullscreen mode
- **M**: Menu (when available)
- **Enter**: Continue after completing levels or game over

### Level Progression

- **Level 1**: 1000m target distance - Learn the basics
- **Level 2**: 1500m target distance - Increase your endurance
- **Level 3**: 2000m target distance - Test your consistency
- **Level 4**: 2500m target distance - Master level challenge

Complete all levels to see the victory screen and your final stats!

### Pro Tips

- **Perfect Timing**: Hit the center of the green zone to restore stamina
- **Rhythm is Key**: Develop a consistent cadence at a high speed
- **Watch Your Stamina**: The green bar in your stamina meter tells you how stamina will be affected if you pedal right now
- **Speed Management**: Higher speeds make timing more challenging

## ⚙️ Configuration

### Basic Game Settings (`client/config.json`)

```json
{
  "window": {
    "width": 800,
    "height": 600,
    "fullscreen": false
  }
}
```

> **Note**: Additional configuration options are available for audio, controls, and game settings. Check the full config file for all options.

### Server Configuration (`.env` file)

```bash
PORT=3000
NODE_ENV=development
ALLOWED_ORIGINS=http://localhost:3000
```

## 🗂️ Project Architecture

```
FixieDashBrooklyn/
├── client/                     # Python/Pygame game client
│   ├── game/                  # Core game modules
│   │   ├── core/             # Game logic (physics, cyclist, timing)
│   │   ├── services/         # Services (game, API, background, config)
│   │   ├── states/           # Game states (menu, game, new game)
│   │   ├── ui/               # UI components and rendering
│   │   ├── container.py      # Dependency injection container
│   │   └── cycling_game.py   # Main game class
│   ├── assets/               # Game assets (images, etc.)
│   ├── main.py              # Application entry point
│   ├── config.json          # Game configuration
│   ├── requirements.txt     # Python dependencies
│   └── setup_dev.py         # Development setup automation
├── server/                   # Node.js/TypeScript server
│   ├── src/
│   │   ├── dao/             # Data access objects
│   │   ├── di/              # Dependency injection setup
│   │   ├── middleware/      # Express middleware
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── types/           # TypeScript definitions
│   │   └── utils/           # Utility functions
│   ├── package.json         # Node.js configuration
│   └── tsconfig.json        # TypeScript configuration
└── README.md               # This file
```

## 🔧 Development

### Client Development

```bash
cd client
python setup_dev.py  # Initial setup
source venv/bin/activate
python main.py       # Run with development features
```

### Server Development

```bash
cd server
npm run dev         # Start with hot reload
npm run build       # Build TypeScript
npm run lint        # Check code style
npm run lint:fix    # Fix linting issues
```

### Code Quality

**Python (Client):**

```bash
pip install black flake8
black .            # Format code
flake8 .          # Check style
```

**TypeScript (Server):**

```bash
npm run lint       # ESLint check
npm run lint:fix   # Auto-fix issues
```

## 🐛 Troubleshooting

### Common Issues

**"ModuleNotFoundError" when running client:**

- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Use setup script: `python setup_dev.py`

**"Port already in use" for server:**

- Kill existing process: `lsof -ti:3000 | xargs kill -9` (macOS/Linux)
- On Windows: `netstat -ano | findstr :3000` then `taskkill /PID <PID> /F`
- Change port in `.env` file

**Game performance issues:**

- Reduce window size in `config.json`
- Close other applications to free up resources
- Check if Python virtual environment is properly activated

**Assets missing:**

- Ensure `assets/` directory exists in client folder
- Check for required image files
- Run setup script to verify assets: `python setup_dev.py`

**Game won't start:**

- Verify Python version: `python --version` (should be 3.8+)
- Check pygame installation: `pip show pygame`
- Look for error messages in terminal output
- Try running from correct directory (`client/`)

### Debug Information

- Press **F12** to show FPS counter and performance info
- Check console output for detailed error messages
- Review `config.json` for syntax errors (JSON format)
- Verify virtual environment is activated (prompt should show `(venv)`)
- Test server connection by visiting `http://localhost:3000/health`

### Performance Optimization

- **Frame Rate**: Use F12 to monitor FPS, aim for 60 FPS
- **Memory**: Restart game if experiencing slowdowns after extended play
- **Network**: Ensure stable connection for multiplayer features

## 📡 API Reference

### Health Check

- `GET /health` - Server status and version info

### User Management

- `POST /api/users/register` - Register new user (username, optional email)
- `GET /api/users/:userId` - Get user profile
- `GET /api/users/:userId/stats` - Get user statistics

### Game Sessions

- `POST /api/game/start` - Start new game session
- `POST /api/game/end` - End session and submit score

### Leaderboards

- `GET /api/leaderboard/top/:limit?` - Get top scores (default limit: 10)

## 🎯 Game Development Notes

### Key Classes and Services

**Client Side:**

- `GameService`: Main game coordination and level management
- `Physics`: Speed, stamina, and movement calculations
- `Cyclist`: Player character state and animation
- `BackgroundService`: Dynamic background rendering
- `APIClient`: Server communication
- `ConfigService`: Settings management

**Server Side:**

- `GameService`: Session management and score processing
- `UserService`: User registration and profiles
- `LeaderboardService`: High score tracking and ranking

### State Management

The game uses a state machine with these main states:

- **MenuState**: User sign-in, leaderboards, game start
- **GameState**: Main gameplay with physics and timing
- **NewGameState**: Simplified game state wrapper

### Game Loop

1. **Input Processing**: Capture pedal timing
2. **Physics Update**: Calculate speed, stamina, distance
3. **Collision Detection**: Check timing zone hits
4. **State Updates**: Progress tracking, level completion
5. **Rendering**: Draw game elements and UI

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Follow code style guidelines (black for Python, ESLint for TypeScript)
5. Update tests if applicable
6. Commit: `git commit -am 'Add feature'`
7. Push: `git push origin feature-name`
8. Submit pull request

### Development Guidelines

- Write clear, descriptive commit messages
- Add comments for complex game logic
- Test on both single-player and multiplayer modes
- Verify changes don't break existing functionality

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built for the Brooklyn cycling community
- Inspired by classic timing-based arcade games
- Thanks to all the local spots that keep us fueled for rides!

---

**Master the rhythm, conquer the streets! 🚴‍♂️⚡**
