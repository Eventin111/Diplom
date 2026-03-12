export const getNextIndex = (currentIndex, itemsLength) => {
  if (itemsLength <= 0) {
    return 0;
  }

  return (currentIndex + 1) % itemsLength;
};

export const getPreviousIndex = (currentIndex, itemsLength) => {
  if (itemsLength <= 0) {
    return 0;
  }

  return (currentIndex - 1 + itemsLength) % itemsLength;
};
