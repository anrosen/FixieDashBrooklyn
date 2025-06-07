import { Router } from 'express';
import { container } from 'tsyringe';
import { LeaderboardService } from '../services/leaderboardService';

const router = Router();
const leaderboardService = container.resolve(LeaderboardService);

// Get top scores
router.get('/top/:limit?', async (req, res) => {
  try {
    const limit = parseInt(req.params.limit || '10');
    const entries = await leaderboardService.getTopScores(limit);
    return res.json({ success: true, entries });
  } catch (error) {
    return res.status(500).json({ error: 'Failed to fetch leaderboard' });
  }
});

export { router as leaderboardRoutes };
