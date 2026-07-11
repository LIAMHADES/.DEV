// Undo/redo with JSON snapshots (max 100)
window.EditorHistory = (function () {
  function create(options) {
    var getState = options.getState;
    var restoreState = options.restoreState;
    var onRestore = options.onRestore || function () {};
    var refreshButtons = options.refreshButtons || function () {};
    var limit = options.limit || 100;

    var undoStack = [];
    var redoStack = [];

    function snapshot() {
      return JSON.stringify(getState());
    }

    function push(snapshotBefore) {
      undoStack.push(snapshotBefore);
      if (undoStack.length > limit) undoStack.shift();
      redoStack = [];
      refreshButtons(undoStack.length > 0, redoStack.length > 0);
    }

    function undo() {
      if (!undoStack.length) return;
      redoStack.push(snapshot());
      restoreState(JSON.parse(undoStack.pop()));
      onRestore();
      refreshButtons(undoStack.length > 0, redoStack.length > 0);
    }

    function redo() {
      if (!redoStack.length) return;
      undoStack.push(snapshot());
      restoreState(JSON.parse(redoStack.pop()));
      onRestore();
      refreshButtons(undoStack.length > 0, redoStack.length > 0);
    }

    function reset() {
      undoStack = [];
      redoStack = [];
      refreshButtons(false, false);
    }

    return { snapshot: snapshot, push: push, undo: undo, redo: redo, reset: reset };
  }

  return { create: create };
})();
