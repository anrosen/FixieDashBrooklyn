import type { Request, Response } from 'express';
import { Router } from 'express';
import { container } from '../di/container';
import { GameService } from '../services/gameService';

const router = Router();
const gameService = container.resolve(GameService);

// Start a new game session (for tracking purposes)
router.post('/start', async (req: Request, res: Response) => {
  try {
    const { playerId } = req.body;
    
    if (!playerId) {
      return res.status(400).json({ 
        error: 'Player ID is required' 
      });
    }

    const sessionId = await gameService.startSession(playerId);
    return res.json({ success: true, sessionId });
  } catch (error) {
    return res.status(500).json({ error: 'Failed to start game session' });
  }
});

// End game session and submit final score
router.post('/end', async (req: Request, res: Response) => {
  try {
    const { sessionId, maxSpeed, totalDistance, completionTime } = req.body;

    if (!sessionId) {
      return res.status(400).json({ 
        error: 'Session ID is required' 
      });
    }

    const result = await gameService.endSession({
      sessionId,
      maxSpeed: maxSpeed || 0,
      totalDistance: totalDistance || 0,
      completionTime: completionTime || 0,
    });

    return res.json({ success: true, result });
  } catch (error) {
    return res.status(500).json({ error: 'Failed to end game session' });
  }
});

export { router as gameRoutes };
