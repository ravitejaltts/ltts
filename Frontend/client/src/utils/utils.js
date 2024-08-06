export function debounce(cb, delay) {
  let timer = null;
  return function (...arg) {
    const context = this;
    clearTimeout(timer);
    timer = setTimeout(() => {
      cb.apply(context, arg);
    }, [delay]);
  };
}

export const numberFormat = (number, maxSignificantDigit = 3) => {
  return new Intl.NumberFormat("en-IN", {
    maximumSignificantDigits: maxSignificantDigit,
  }).format(number);
};
