import { ChangeEvent, FormEvent, useMemo, useState } from 'react';
import { uploadMedia } from '../api';
import { DetectionResult } from '../types';

type Props = {
  onStart: () => void;
  onComplete: (result: DetectionResult) => void;
  onError: (message: string) => void;
};

const ACCEPTED_TYPES = [
  'image/png',
  'image/jpeg',
  'image/webp',
  'video/mp4',
  'video/quicktime',
  'video/webm'
];

function UploadForm({ onStart, onComplete, onError }: Props) {
  const [file, setFile] = useState<File | null>(null);

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selected = event.target.files?.[0];
    setFile(selected ?? null);
  };

  const isVideo = useMemo(() => file?.type.startsWith('video/'), [file]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!file) {
      onError('Please select a file to upload.');
      return;
    }

    if (!ACCEPTED_TYPES.includes(file.type)) {
      onError('Unsupported file type.');
      return;
    }

    try {
      onStart();
      const result = await uploadMedia(file, isVideo ? 'video' : 'image');
      onComplete(result);
    } catch (error) {
      console.error(error);
      onError('Failed to run detection. Please try again.');
    }
  };

  return (
    <form className="upload-form" onSubmit={handleSubmit}>
      <label className="file-input">
        <span>Select media</span>
        <input type="file" accept={ACCEPTED_TYPES.join(',')} onChange={handleChange} />
      </label>
      {file && (
        <p className="file-meta">
          Selected: <strong>{file.name}</strong> ({Math.round(file.size / 1024)} KB)
        </p>
      )}
      <button type="submit" disabled={!file}>
        Run Detection
      </button>
    </form>
  );
}

export default UploadForm;
