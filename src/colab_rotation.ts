/**
 * 5 Colab Profiles Round-Robin Load Balancer
 */
export function getNextColabProfileIndex(): number {
  // Use timestamp milliseconds to pick round-robin profile index 1, 2, 3, 4, or 5 evenly
  return (Math.floor(Date.now() / 1000) % 5) + 1;
}
