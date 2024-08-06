const ls = {
  setItem: (name, value) => {
    localStorage.setItem(name, value);
  },
  getItem: (name) => {
    return localStorage.getItem(name);
  },
};

export default ls;
