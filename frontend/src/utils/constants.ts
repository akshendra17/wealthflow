/**
 * Category constants — icons, colors, and display configuration.
 */

export const CATEGORY_CONFIG: Record<string, { icon: string, color: string, gradient: string }> = {
  Food:        { icon: '🍔', color: '#ff6b6b', gradient: 'linear-gradient(135deg, #ff6b6b, #ee5a24)' },
  Grocery:     { icon: '🛒', color: '#51cf66', gradient: 'linear-gradient(135deg, #51cf66, #20bf6b)' },
  Loans:       { icon: '🏦', color: '#ff922b', gradient: 'linear-gradient(135deg, #ff922b, #f76707)' },
  EMI:         { icon: '💳', color: '#f06595', gradient: 'linear-gradient(135deg, #f06595, #e64980)' },
  Clothing:    { icon: '👕', color: '#cc5de8', gradient: 'linear-gradient(135deg, #cc5de8, #ae3ec9)' },
  Leisure:     { icon: '🎮', color: '#339af0', gradient: 'linear-gradient(135deg, #339af0, #1c7ed6)' },
  Shopping:    { icon: '🛍️', color: '#20c997', gradient: 'linear-gradient(135deg, #20c997, #0ca678)' },
  Transport:   { icon: '🚗', color: '#fcc419', gradient: 'linear-gradient(135deg, #fcc419, #f59f00)' },
  Utilities:   { icon: '💡', color: '#748ffc', gradient: 'linear-gradient(135deg, #748ffc, #5c7cfa)' },
  Health:      { icon: '🏥', color: '#f783ac', gradient: 'linear-gradient(135deg, #f783ac, #e64980)' },
  Rent:        { icon: '🏠', color: '#e599f7', gradient: 'linear-gradient(135deg, #e599f7, #cc5de8)' },
  Investments: { icon: '📈', color: '#38d9a9', gradient: 'linear-gradient(135deg, #38d9a9, #20c997)' },
  Misc:        { icon: '📦', color: '#859399', gradient: 'linear-gradient(135deg, #859399, #6b7b82)' },
};

export const MONTH_NAMES = [
  '', 'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

export const MONTH_SHORT = [
  '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
];

export const BANK_OPTIONS = [
  { label: 'All Banks', value: '' },
  { label: 'HDFC Bank', value: 'hdfc' },
  { label: 'Axis Bank', value: 'axis' },
  { label: 'ICICI Bank', value: 'icici' },
  { label: 'SBI', value: 'sbi' },
  { label: 'HSBC', value: 'hsbc' },
  { label: 'Bank of India (BOI)', value: 'boi' },
  { label: 'Bank of Baroda (BOB)', value: 'bob' },
  { label: 'Kotak Mahindra', value: 'kotak' },
  { label: 'Canara Bank', value: 'canara' },
  { label: 'American Express', value: 'amex' },
];
