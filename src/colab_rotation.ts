/**
 * Colab Profiles Round-Robin Load Balancer
 * Currently configured for 2 profiles testing (Profile #1 & Profile #2)
 */
export function getNextColabProfileIndex(): number {
  // Rotate between Profile 1 and Profile 2 for initial testing stage
  return (Math.floor(Date.now() / 1000) % 2) + 1;
}
