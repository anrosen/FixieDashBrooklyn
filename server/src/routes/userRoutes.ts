import type { Request, Response } from 'express';
import { Router } from 'express';
import { container } from '../di/container';
import { UserService } from '../services/userService';

const router = Router();
const userService = container.resolve(UserService);

// Register a new user
router.post('/register', async (req: Request, res: Response) => {
  try {
    const { username, email } = req.body;
    
    if (!username) {
      return res.status(400).json({ 
        error: 'Username is required' 
      });
    }

    const user = await userService.createUser({ username, email });
    return res.json({ success: true, user });
  } catch (error) {
    return res.status(500).json({ error: 'Failed to create user' });
  }
});

// Get user profile
router.get('/:userId', async (req: Request, res: Response) => {
  try {
    const { userId } = req.params;
    const user = await userService.getUser(userId);
    
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    return res.json({ success: true, user });
  } catch (error) {
    return res.status(500).json({ error: 'Failed to fetch user' });
  }
});

export { router as userRoutes };
