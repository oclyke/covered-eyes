/* eslint-disable no-restricted-syntax */
export default class KVStore {
  constructor() {
    this.items = new Map();
    this.validations = new Map();
    this.subscriptions = new Map();

    this.initialize();
  }

  /**
   * Synchronous method for validating a key
   */
  validate(key) {
    this.validations.set(key, true);
  }

  /**
   * Synchronous method for invalidating a key
   */
  invalidate(key) {
    this.validations.set(key, false);
  }

  /**
   * Synchronous method for extracting a value by key.
   * Throws an error if the key was undefined.
   * @param {*} key used to get data from cache items.
   */
  extract(key) {
    const valid = this.validations.get(key);
    if (typeof valid === 'undefined') {
      throw new Error('cache miss [nonexistent]');
    }
    if (valid !== true) {
      throw new Error('cache miss [invalid]');
    }
    const data = this.items.get(key);
    return data;
  }

  /**
   * Synchronous method for storing value by key.
   * @param {*} key
   * @param {*} value
   */
  store(key, value) {
    this.items.set(key, value);
    this.validate(key);
    this.notify(key);
    return [key, value];
  }

  /**
   * Async method for getting value by key.
   * @param {*} key
   * @returns
   */
  get(key) {
    return new Promise((resolve, reject) => {
      try {
        const data = this.extract(key);
        resolve(data);
      } catch (e) {
        reject(e);
      }
    });
  }

  /**
   * Async method for storing value by key.
   * @param {*} key
   * @param {*} value
   * @returns
   */
  put(key, value) {
    return new Promise((resolve, reject) => {
      try {
        const data = this.store(key, value);
        resolve(data);
      } catch (e) {
        reject(e);
      }
    });
  }

  initialize() {
    this.items = new Map();
    this.validations = new Map();
    return Promise.resolve();
  }

  /**
   * Alows for subscribing to cache updates.
   * The callback is called with the key and the new value when the value is updated.
   * @param {*} key
   * @param {*} callback
   * @returns
   */
  subscribe(key, callback) {
    let subs = this.subscriptions.get(key);
    if (typeof subs === 'undefined') {
      subs = new Map();
      this.subscriptions.set(key, subs);
    }
    subs.set(key, callback);
  }

  /**
   * Allows for unsubscribing from cache updates.
   * @param {*} key
   * @param {*} callback
   * @returns
   */
  unsubscribe(key, callback) {
    const subs = this.subscriptions.get(key);
    if (typeof subs === 'undefined') {
      return;
    }
    subs.delete(callback);
  }

  /**
   * Notifies all subscribers of a cache update.
   * @param {*} key the key of the cache update.
   * @returns
   */
  notify(key) {
    const subscribed = this.subscriptions.get(key);
    if (typeof subscribed === 'undefined') {
      return;
    }
    const value = this.extract(key);
    subscribed.forEach((listener) => listener(key, value));
  }
}
