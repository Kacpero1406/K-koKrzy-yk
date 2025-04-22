from flask import Flask, request, jsonify, render_template_string
import copy

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Tic Tac Toe</title>
  <style>
    body {
      font-family: 'Segoe UI', sans-serif;
      text-align: center;
      background: #f7f7f7;
      padding: 20px;
    }
    h1 { color: #333; }
    .board {
      display: grid;
      grid-template-columns: repeat(3, 100px);
      gap: 10px;
      margin: 20px auto;
    }
    .cell {
      width: 100px;
      height: 100px;
      font-size: 2.5em;
      font-weight: bold;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #fff;
      border: 2px solid #ccc;
      border-radius: 10px;
      cursor: pointer;
      transition: background 0.2s;
    }
    .cell:hover {
      background: #eaeaea;
    }
    .status {
      margin-top: 20px;
      font-size: 1.2em;
      font-weight: bold;
    }
    .btn {
      margin-top: 15px;
      padding: 10px 20px;
      font-size: 1em;
      background: #007bff;
      color: white;
      border: none;
      border-radius: 10px;
      cursor: pointer;
    }
    .btn:hover {
      background: #0056b3;
    }
  </style>
</head>
<body>
  <h1>Kółko i Krzyżyk</h1>
  <div class="board" id="board"></div>
  <div class="status" id="status"></div>
  <button class="btn" onclick="resetGame()">Zagraj ponownie</button>

  <script>
    let board = [["", "", ""], ["", "", ""], ["", "", ""]];
    let gameOver = false;

    const boardDiv = document.getElementById("board");
    const statusDiv = document.getElementById("status");

    function drawBoard() {
      boardDiv.innerHTML = "";
      board.forEach((row, i) => {
        row.forEach((cell, j) => {
          const div = document.createElement("div");
          div.className = "cell";
          div.textContent = cell;
          div.onclick = () => handleMove(i, j);
          boardDiv.appendChild(div);
        });
      });
    }

    function handleMove(i, j) {
      if (board[i][j] !== "" || gameOver) return;
      board[i][j] = "O";
      drawBoard();
      checkGameOver();

      fetch("/move", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ board }),
      })
      .then(res => res.json())
      .then(data => {
        board = data.board;
        drawBoard();
        if (data.winner) {
          statusDiv.textContent = data.winner === "draw" ? "Remis!" : `Wygrał: ${data.winner}`;
          gameOver = true;
        }
      });
    }

    function checkGameOver() {
      fetch("/check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ board }),
      })
      .then(res => res.json())
      .then(data => {
        if (data.winner) {
          statusDiv.textContent = data.winner === "draw" ? "Remis!" : `Wygrał: ${data.winner}`;
          gameOver = true;
        }
      });
    }

    function resetGame() {
      board = [["", "", ""], ["", "", ""], ["", "", ""]];
      gameOver = false;
      statusDiv.textContent = "";
      drawBoard();
    }

    drawBoard();
  </script>
</body>
</html>
"""

def check_winner(board):
    for i in range(3):
        if board[i][0] != "" and all(board[i][j] == board[i][0] for j in range(3)):
            return board[i][0]
        if board[0][i] != "" and all(board[j][i] == board[0][i] for j in range(3)):
            return board[0][i]
    if board[0][0] != "" and all(board[i][i] == board[0][0] for i in range(3)):
        return board[0][0]
    if board[0][2] != "" and all(board[i][2 - i] == board[0][2] for i in range(3)):
        return board[0][2]
    return None

def is_full(board):
    return all(cell != "" for row in board for cell in row)

def minimax(board, is_maximizing):
    winner = check_winner(board)
    if winner == "X":
        return 1
    elif winner == "O":
        return -1
    elif is_full(board):
        return 0

    if is_maximizing:
        best_score = -float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j] == "":
                    board[i][j] = "X"
                    score = minimax(board, False)
                    board[i][j] = ""
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j] == "":
                    board[i][j] = "O"
                    score = minimax(board, True)
                    board[i][j] = ""
                    best_score = min(score, best_score)
        return best_score

def best_move(board):
    best_score = -float('inf')
    move = None
    for i in range(3):
        for j in range(3):
            if board[i][j] == "":
                board[i][j] = "X"
                score = minimax(board, False)
                board[i][j] = ""
                if score > best_score:
                    best_score = score
                    move = (i, j)
    return move

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/move", methods=["POST"])
def move():
    data = request.json
    board = data["board"]

    if check_winner(board) or is_full(board):
        return jsonify({"board": board, "winner": check_winner(board) or "draw"})

    move = best_move(copy.deepcopy(board))
    if move:
        i, j = move
        board[i][j] = "X"

    winner = check_winner(board)
    if winner:
        return jsonify({"board": board, "winner": winner})
    elif is_full(board):
        return jsonify({"board": board, "winner": "draw"})

    return jsonify({"board": board})

@app.route("/check", methods=["POST"])
def check():
    board = request.json["board"]
    winner = check_winner(board)
    if winner:
        return jsonify({"winner": winner})
    elif is_full(board):
        return jsonify({"winner": "draw"})
    return jsonify({"winner": None})

if __name__ == "__main__":
    app.run(debug=True)
