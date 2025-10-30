import axios from 'axios';
import { DetectionResult } from './types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function uploadMedia(file: File, kind: 'image' | 'video'): Promise<DetectionResult> {
  const formData = new FormData();
  formData.append('file', file);

  const endpoint = kind === 'image' ? '/detect/image' : '/detect/video';
  const response = await axios.post<DetectionResult>(`${API_BASE}${endpoint}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}
