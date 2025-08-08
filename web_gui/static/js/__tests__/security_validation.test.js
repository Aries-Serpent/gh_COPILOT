// Primary Copilot: test basic input sanitization.
// Secondary Copilot: verify sanitized output.
import { validateSecurity } from '../security_validation.js';

test('validateSecurity strips angle brackets', () => {
  const result = validateSecurity('<script>');
  expect(result).toBe('script');
});
