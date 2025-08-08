// Primary Copilot: perform basic input sanitization.
// Secondary Copilot: report validation success to console.

export function validateSecurity(input = '') {
  const sanitized = input.replace(/[<>]/g, '');
  console.debug('Security validation passed', sanitized === input);
  return sanitized;
}
