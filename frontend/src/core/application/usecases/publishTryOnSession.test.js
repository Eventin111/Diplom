import { publishTryOnSession } from './publishTryOnSession';

describe('publishTryOnSession usecase', () => {
  it('passes explicit publish params to repository', async () => {
    const publish = jest.fn().mockResolvedValue({ id: 7 });
    const repository = {
      publishTryOnSession: publish
    };

    const result = await publishTryOnSession(repository, 15, {
      caption: 'new look',
      sourceType: 'post',
      sourcePostId: 101,
      hashtags: ['look', 'spring']
    });

    expect(result).toEqual({ id: 7 });
    expect(publish).toHaveBeenCalledWith(15, {
      caption: 'new look',
      sourceType: 'post',
      sourcePostId: 101,
      hashtags: ['look', 'spring']
    });
  });

  it('uses defaults when options are omitted', async () => {
    const publish = jest.fn().mockResolvedValue({ ok: true });
    const repository = {
      publishTryOnSession: publish
    };

    await publishTryOnSession(repository, 42);

    expect(publish).toHaveBeenCalledWith(42, {
      caption: '',
      sourceType: null,
      sourcePostId: null,
      hashtags: []
    });
  });
});
