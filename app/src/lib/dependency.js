/* eslint-disable no-restricted-syntax */
export default class DependencyGraph {
  constructor() {
    this.dependencies = new Map();
    this.dependents = new Map();
    this.nodes = new Set();
  }

  /**
   * Clone a dependency graph.
   * @returns a new dependency graph with the same nodes and connections as this one.
   */
  clone() {
    const cloned = new DependencyGraph();
    cloned.dependencies = DependencyGraph.copyDepmap(this.dependencies);
    cloned.dependents = DependencyGraph.copyDepmap(this.dependents);
    cloned.nodes = new Set(this.nodes);
    return cloned;
  }

  /**
   * Copy a dependency map.
   * @param {*} map
   * @returns a new map with the same keys and values as the given map.
   */
  static copyDepmap(map) {
    const out = new Map();
    for (const [key, value] of map.entries()) {
      out.set(key, new Set(value));
    }
    return out;
  }

  /**
   * Remove a node from a nodeset in a map of nodesets keyed by a string.
   * @param {*} map
   * @param {*} key
   * @param {*} node
   */
  static removeFromDepmap(map, key, node) {
    const nodes = map.get(key);
    if (nodes.size === 1) {
      map.delete(key);
    } else {
      nodes.delete(node);
    }
  }

  /**
   * Add a node to a nodeset in a map of nodesets keyed by a string
   * @param {*} map the nodeset to which the node should be added
   * @param {*} key the key indicating which dependency the node should be added to
   * @param {*} node the node being added
   */
  static addNodeToNodeset(map, key, node) {
    let nodes = map.get(key);
    if (typeof nodes === 'undefined') {
      nodes = new Set();
      map.set(key, nodes);
    }
    nodes.add(node);
  }

  /**
   * Register a dependency between two nodes
   * @param {*} child the node that depends on the parent
   * @param {*} parent the node that the child depends on
   */
  dependOn(child, parent) {
    if (child === parent) {
      throw new Error('self-referential dependencies not allowed');
    }
    if (this.dependsOn(parent, child)) {
      throw new Error('circular dependencies not allowed');
    }

    // ensure the nodes are present
    this.nodes.add(child);
    this.nodes.add(parent);

    // add the connections between nodes
    DependencyGraph.addNodeToNodeset(this.dependents, parent, child);
    DependencyGraph.addNodeToNodeset(this.dependencies, child, parent);
  }

  /**
   * Test whether the child depends on the parent
   * @param {*} child the child node
   * @param {*} parent the parent node
   * @returns true if the child depends on the parent, false otherwise
   */
  dependsOn(child, parent) {
    const dependecies = this.getDependencies(child);
    return dependecies.has(parent);
  }

  /**
   * Get the set of nodes that the given node depends on
   * @param {*} node the node whose dependencies should be returned
   * @returns the set of nodes that the given node depends on
   */
  getDependencies(node) {
    const out = new Set();

    // start searching from this node
    // searchNext is updated with discovered dependencies
    let searchNext = [node];

    while (searchNext.length > 0) {
      // maintain a list of discovered dependencies
      const discovered = [];
      for (const searchNode of searchNext) {
        const nextNodes = this.dependencies.get(searchNode) || new Set();
        for (const nextNode of nextNodes) {
          if (!out.has(nextNode)) {
            out.add(nextNode);
            discovered.push(nextNode);
          }
        }
      }

      // update the search list with the newly discovered dependencies
      searchNext = discovered;
    }

    return out;
  }

  /**
   * Get the set of nodes that are dependent on the given node
   * @param {*} node the node whose dependents should be returned
   * @returns the set of nodes that are dependent on the given node
   */
  getDependents(node) {
    const out = new Set();

    // start searching from this node
    // searchNext is updated with discovered dependents
    let searchNext = [node];

    while (searchNext.length > 0) {
      // maintain a list of discovered dependents
      const discovered = [];
      for (const searchNode of searchNext) {
        const nextNodes = this.dependents.get(searchNode) || new Set();
        for (const nextNode of nextNodes) {
          if (!out.has(nextNode)) {
            out.add(nextNode);
            discovered.push(nextNode);
          }
        }
      }

      // update the search list with the newly discovered dependencies
      searchNext = discovered;
    }

    return out;
  }

  /**
   * Return the leaves of the graph - the nodes that have no dependencies.
   * @returns the set of nodes that have no dependencies.
   */
  leaves() {
    const leaves = [];

    for (const node of this.nodes) {
      if (!this.dependencies.has(node)) {
        leaves.push(node);
      }
    }

    return leaves;
  }

  /**
   * Remove a node from the graph.
   * @param {*} node the node to remove.
   */
  remove(node) {
    for (const dependent of this.dependents.get(node) || new Set()) {
      DependencyGraph.removeFromDepmap(this.dependencies, dependent, node);
    }
    this.dependents.delete(node);

    for (const dependency of this.dependencies.get(node) || new Set()) {
      DependencyGraph.removeFromDepmap(this.dependents, dependency, node);
    }
    this.dependencies.delete(node);

    this.nodes.delete(node);
  }

  /**
   * Sort the nodes in the graph into layers, where each layer is an array of
   * nodes that have no dependencies on nodes in the previous layer.
   *
   * @returns an array of layers, where each layer is an array of nodes that
   * have no dependencies on nodes in the previous layer.
   */
  topoSortedLayers() {
    const layers = [];
    const shrinkingGraph = this.clone();

    // eslint-disable-next-line no-constant-condition
    while (true) {
      const leaves = shrinkingGraph.leaves();
      if (leaves.length === 0) {
        break;
      }

      layers.push(leaves);
      for (const leafNode of leaves) {
        shrinkingGraph.remove(leafNode);
      }
    }

    return layers;
  }
}

function layersEquivalent(xs, ys) {
  return (
    xs.length === ys.length
    && [...xs].every((x) => ys.includes(x)));
}

function testCircularReference() {
  const g = new DependencyGraph();
  try {
    g.dependOn('a', 'b');
    g.dependOn('b', 'c');
    g.dependOn('c', 'a');
    return false;
  } catch (err) {
    return true;
  }
}

function testSelfReference() {
  const g = new DependencyGraph();
  try {
    g.dependOn('a', 'a');
    return false;
  } catch (err) {
    return true;
  }
}

function testSort() {
  // specify the expected layers
  const expectedLayers = [
    ['soil', 'water'],
    ['grain'],
    ['chickens', 'flour'],
    ['eggs'],
    ['cake'],
  ];

  // creat a dependency graph
  const g = new DependencyGraph();

  // add the dependencies
  g.dependOn('cake', 'eggs');
  g.dependOn('cake', 'flour');
  g.dependOn('eggs', 'chickens');
  g.dependOn('flour', 'grain');
  g.dependOn('chickens', 'grain');
  g.dependOn('grain', 'soil');
  g.dependOn('grain', 'water');
  g.dependOn('chickens', 'water');

  // print some information about dependencies
  console.log('cake depends on', g.getDependencies('cake'));
  console.log('cake is depended on by', g.getDependents('cake'));

  console.log('grain depends on', g.getDependencies('grain'));
  console.log('grain is depended on by', g.getDependents('grain'));

  console.log('soil depends on', g.getDependencies('soil'));
  console.log('soil is depended on by', g.getDependents('soil'));

  // sort the layers
  const layers = g.topoSortedLayers();

  if (layers.length !== expectedLayers.length) {
    return false;
  }
  for (let i = 0; i < layers.length; i += 1) {
    const layer = layers[i];
    const expected = expectedLayers[i];
    if (!layersEquivalent(layer, expected)) {
      return false;
    }
  }
  return true;
}

// eslint-disable-next-line no-unused-vars
function runTests() {
  const tests = [
    testSelfReference,
    testCircularReference,
    testSort,
  ];
  for (const test of tests) {
    console.log('running test', test.name);
    const result = test();
    if (!result) {
      throw new Error('test failed');
    }
  }
}
