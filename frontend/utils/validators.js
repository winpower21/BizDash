// frontend/utils/validators.js
export const validatePhone = (phoneNumber) => {
    if (!phoneNumber) return ''; // Allow empty for optional fields.
    const phoneStr = String(phoneNumber);
    if (!/^\d+$/.test(phoneStr)) return 'Only digits are allowed';
    if (phoneStr.startsWith('0')) return 'Phone number cannot start with 0';
    if (phoneStr.length !== 10) return 'Phone number must be exactly 10 digits';
    return ''; // No error
};
