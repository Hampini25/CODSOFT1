import sys

# Flask is optional for running quick tests. Import lazily when available.
try:
  from flask import Flask, request, jsonify, render_template_string
  HAS_FLASK = True
except Exception:
  HAS_FLASK = False

# ------------------ CONSTANTS ------------------
HUMAN = "X"
AI = "O"
EMPTY = ""

# ------------------ CORE AI / HELPERS ------------------

def check_winner(board):
    # rows
    for r in range(3):
        if board[r][0] != EMPTY and board[r][0] == board[r][1] == board[r][2]:
            return board[r][0], [(r, 0), (r, 1), (r, 2)]
    # cols
    for c in range(3):
        if board[0][c] != EMPTY and board[0][c] == board[1][c] == board[2][c]:
            return board[0][c], [(0, c), (1, c), (2, c)]
    # diags
    if board[0][0] != EMPTY and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0], [(0, 0), (1, 1), (2, 2)]
    if board[0][2] != EMPTY and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2], [(0, 2), (1, 1), (2, 0)]

    return None, []


def validate_board(board):
    """Ensure board is a 3x3 list of lists with allowed symbols."""
    if not isinstance(board, list) or len(board) != 3:
        return False
    for row in board:
        if not isinstance(row, list) or len(row) != 3:
            return False
        for cell in row:
            if cell not in (EMPTY, HUMAN, AI):
                return False
    return True


def is_full(board):
    for r in range(3):
        for c in range(3):
            if board[r][c] == EMPTY:
                return False
    return True


def minimax(board, depth, is_maximizing, alpha, beta):
    winner, _ = check_winner(board)
    if winner == AI:
        return 1
    if winner == HUMAN:
        return -1
    if is_full(board):
        return 0

    if is_maximizing:
        best = -999
        for r in range(3):
            for c in range(3):
                if board[r][c] == EMPTY:
                    board[r][c] = AI
                    val = minimax(board, depth + 1, False, alpha, beta)
                    board[r][c] = EMPTY
                    best = max(best, val)
                    alpha = max(alpha, best)
                    if beta <= alpha:
                        return best
        return best
    else:
        best = 999
        for r in range(3):
            for c in range(3):
                if board[r][c] == EMPTY:
                    board[r][c] = HUMAN
                    val = minimax(board, depth + 1, True, alpha, beta)
                    board[r][c] = EMPTY
                    best = min(best, val)
                    beta = min(beta, best)
                    if beta <= alpha:
                        return best
        return best


def find_best_move(board):
  # 1) take immediate winning move
  for r in range(3):
    for c in range(3):
      if board[r][c] == EMPTY:
        board[r][c] = AI
        winner, _ = check_winner(board)
        board[r][c] = EMPTY
        if winner == AI:
          return (r, c)

  # 2) block opponent immediate win
  for r in range(3):
    for c in range(3):
      if board[r][c] == EMPTY:
        board[r][c] = HUMAN
        winner, _ = check_winner(board)
        board[r][c] = EMPTY
        if winner == HUMAN:
          return (r, c)

  # 3) otherwise use minimax with deterministic preferences
  best_val = -999
  best_move = None
  preferred = [(1, 1), (0, 0), (0, 2), (2, 0), (2, 2), (0, 1), (1, 0), (1, 2), (2, 1)]
  for r, c in preferred:
    if board[r][c] == EMPTY:
      board[r][c] = AI
      move_val = minimax(board, 0, False, -999, 999)
      board[r][c] = EMPTY
      if move_val > best_val:
        best_val = move_val
        best_move = (r, c)
        if best_val == 1:
          break
  return best_move

# ------------------ FLASK APP ------------------
if HAS_FLASK:
  app = Flask(__name__)

INDEX_HTML = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Tic Tac Toe - Single File App</title>
  <style>
    :root{--size:84px;--gap:10px}
    body{font-family:Inter,Arial,Helvetica,sans-serif;display:flex;min-height:100vh;align-items:center;justify-content:center;background:linear-gradient(180deg,#f0f7ff,#ffffff)}
    .container{width:480px;padding:22px;border-radius:12px;background:#fff;box-shadow:0 10px 30px rgba(2,6,23,0.08)}
    h1{margin:0 0 10px;font-weight:700;color:#0b2b4a}
    .controls{display:flex;align-items:center;gap:8px;margin-bottom:14px}
    #status{margin-left:auto;font-weight:700;color:#333}
    .score{display:flex;gap:12px;align-items:center;margin-left:8px}
    .score .item{background:#f6fbff;padding:6px 10px;border-radius:8px;font-weight:700;color:#0b2b4a}
    .board{display:grid;grid-template-columns:repeat(3, var(--size));gap:var(--gap);justify-content:center}
    .cell{width:var(--size);height:var(--size);display:flex;align-items:center;justify-content:center;font-size:36px;background:linear-gradient(180deg,#ffffff,#f3f6fb);border-radius:10px;cursor:pointer;user-select:none;transition:transform .08s ease, background .12s ease, box-shadow .08s}
    .cell:hover{transform:translateY(-4px);box-shadow:0 6px 18px rgba(13,38,76,0.08)}
    .cell.disabled{opacity:0.7;cursor:default}
    .cell.win{background:#90EE90}
    .cell.last{outline:3px solid #ffd54d}
    .footer{display:flex;justify-content:space-between;align-items:center;margin-top:12px;color:#64748b}
    .toast{position:fixed;left:50%;transform:translateX(-50%);bottom:18px;background:#0b2b4a;color:#fff;padding:8px 14px;border-radius:8px;box-shadow:0 8px 20px rgba(11,43,74,0.12);display:none}
  </style>
</head>
<body>
  <div class="container">
    <h1>Tic Tac Toe</h1>
    <div class="controls">
      <label>Who starts?</label>
      <select id="firstSelect">
        <option value="human">You</option>
        <option value="ai">AI</option>
      </select>
      <button id="startBtn">New Round</button>
      <button id="restartBtn">Reset Scores</button>
      <div class="score">
        <div class="item">You: <span id="scoreX">0</span></div>
        <div class="item">AI: <span id="scoreO">0</span></div>
        <div class="item">Ties: <span id="scoreT">0</span></div>
      </div>
      <div id="status">Ready</div>
    </div>

    <div id="board" class="board"></div>
  </div>

  <script>
    let boardEl = document.getElementById('board')
    let statusEl = document.getElementById('status')
    let startBtn = document.getElementById('startBtn')
    let restartBtn = document.getElementById('restartBtn')
    let firstSelect = document.getElementById('firstSelect')
    let scoreXEl = document.getElementById('scoreX')
    let scoreOEl = document.getElementById('scoreO')
    let scoreTEl = document.getElementById('scoreT')
    let board = []
    let scoreX = 0, scoreO = 0, scoreT = 0
    const toast = (()=>{const t=document.createElement('div');t.className='toast';document.body.appendChild(t);return t})()

    function showToast(msg, ms=1500){
      toast.textContent = msg; toast.style.display='block'; clearTimeout(toast._t);
      toast._t = setTimeout(()=>toast.style.display='none', ms)
    }

    function renderBoard() {
      boardEl.innerHTML = ''
      for (let r = 0; r < 3; r++) {
        for (let c = 0; c < 3; c++) {
          const div = document.createElement('div')
          div.className = 'cell'
          if (board[r][c] !== '') div.classList.add('disabled')
          div.dataset.r = r
          div.dataset.c = c
          div.textContent = board[r][c]
          div.addEventListener('click', onCellClick)
          boardEl.appendChild(div)
        }
      }
    }

    let gameOver = false
    let lastEl = null

    function clearHighlights() {
      for (const el of boardEl.children) {
        el.classList.remove('win', 'last')
      }
      lastEl = null
    }

    async function onCellClick(e) {
      const r = parseInt(e.currentTarget.dataset.r)
      const c = parseInt(e.currentTarget.dataset.c)
      if (board[r][c] !== '' || gameOver) return
      board[r][c] = 'X'
      renderBoard()
      // mark last move
      const idx = r*3 + c
      const el = boardEl.children[idx]
      if(lastEl) lastEl.classList.remove('last')
      if(el) { el.classList.add('last'); lastEl = el }
      statusEl.textContent = 'AI Thinking...'
      try{
        const resp = await fetch('/move', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({board})
        })
        if(!resp.ok){ const err = await resp.json().catch(()=>({error:'bad'})); showToast(err.error||'Server error'); return }
        var data = await resp.json()
      }catch(e){ showToast('Network or server error'); return }
      board = data.board
      renderBoard()
      // apply last/ win highlights
      if (data.ai_move) {
        const [ar,ac] = data.ai_move
        const aidx = ar*3 + ac
        const ael = boardEl.children[aidx]
        if(lastEl) lastEl.classList.remove('last')
        if(ael){ ael.classList.add('last'); lastEl = ael }
      }
      if (data.winner) {
        statusEl.textContent = data.winner === 'X' ? 'You Win!' : 'AI Wins!'
        highlightCombo(data.combo)
        gameOver = true
        if(data.winner==='X'){ scoreX++ ; scoreXEl.textContent=scoreX } else { scoreO++; scoreOEl.textContent=scoreO }
        showToast(data.winner==='X' ? 'You win 🎉' : 'AI wins')
      } else if (data.tie) {
        statusEl.textContent = "It's a tie"
        gameOver = true
        scoreT++; scoreTEl.textContent=scoreT
        showToast("Tie")
      } else {
        statusEl.textContent = 'Your Turn'
      }
    }

    function highlightCombo(combo){
      if(!combo) return
      for(const [r,c] of combo){
        const idx = r*3 + c
        const el = boardEl.children[idx]
        if(el) el.classList.add('win')
      }
    }

    async function startGame(){
      const first = firstSelect.value
      const resp = await fetch('/start', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({first})})
      if(!resp.ok){ showToast('Server error'); return }
      const data = await resp.json()
      board = data.board
      clearHighlights()
      renderBoard()
      gameOver = false
      if(data.ai_move){
        statusEl.textContent = 'AI moved. Your Turn'
        const [ar,ac] = data.ai_move
        const aidx = ar*3 + ac
        const ael = boardEl.children[aidx]
        if(ael){ ael.classList.add('last'); lastEl = ael }
      } else {
        statusEl.textContent = 'Your Turn'
      }
    }

    startBtn.addEventListener('click', startGame)
    restartBtn.addEventListener('click', ()=>{ scoreX=0;scoreO=0;scoreT=0; scoreXEl.textContent=0;scoreOEl.textContent=0;scoreTEl.textContent=0; showToast('Scores reset') })

    // init
    board = [['','',''],['','',''],['','','']]
    renderBoard()
  </script>
</body>
</html>
'''

if HAS_FLASK:
    @app.route('/')
    def index():
        return render_template_string(INDEX_HTML)

    @app.route('/start', methods=['POST'])
    def start_game():
      try:
        data = request.get_json() or {}
      except Exception:
        return jsonify({'error': 'Invalid JSON'}), 400
      first = data.get('first', 'human')
      board = [[EMPTY for _ in range(3)] for _ in range(3)]
      if first == 'ai':
        mv = find_best_move(board)
        if mv:
          r, c = mv
          board[r][c] = AI
          mv_list = list(mv)
        else:
          mv_list = None
        return jsonify({'board': board, 'ai_move': mv_list})
      return jsonify({'board': board, 'ai_move': None})

    @app.route('/move', methods=['POST'])
    def make_move():
        try:
            data = request.get_json()
        except Exception:
            return jsonify({'error': 'Invalid JSON'}), 400
        board = data.get('board')
        if not validate_board(board):
            return jsonify({'error': 'Invalid board format'}), 400

        winner, combo = check_winner(board)
        if winner:
            combo_list = [list(p) for p in combo]
            return jsonify({'board': board, 'winner': winner, 'combo': combo_list})

        if is_full(board):
            return jsonify({'board': board, 'winner': None, 'tie': True})

        mv = find_best_move(board)
        mv_list = None
        if mv:
            r, c = mv
            board[r][c] = AI
            mv_list = list(mv)

        winner, combo = check_winner(board)
        tie = is_full(board) and winner is None
        # convert combo tuples to lists for JSON consistency
        combo_list = [list(p) for p in combo]
        return jsonify({'board': board, 'ai_move': mv_list, 'winner': winner, 'combo': combo_list, 'tie': tie})


# ------------------ Optional Test Hook ------------------
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # simple smoke tests
        def assert_eq(a,b):
            assert a==b, f"{a} != {b}"

        # AI should take center on empty board
        b = [[EMPTY]*3 for _ in range(3)]
        mv = find_best_move(b)
        print('Best on empty:', mv)
        assert_eq(mv, (1,1))

        # AI blocks
        b = [["X","X",""],["","",""],["","",""]]
        mv = find_best_move(b)
        print('Block move:', mv)
        assert_eq(mv, (0,2))

        print('All quick tests passed')
    else:
        # Run server
        app.run(host='0.0.0.0', port=5000, debug=True)
