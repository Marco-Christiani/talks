import express from "express"
import { createServer } from "http"
import { WebSocketServer } from "ws"
import { spawn } from "node-pty"

const app = express()
const server = createServer(app)
const wss = new WebSocketServer({ server })

wss.on("connection", (ws) => {
  console.log("Connection established")
  const shell = process.env.SHELL || "bash"
  const ptyProcess = spawn(shell, [], {
    cols: 110,
    cwd: "..",
  })

  ptyProcess.onData((data) => ws.send(data))
  ws.on("message", (msg) => ptyProcess.write(msg.toString()))
  ws.on("close", () => ptyProcess.kill())
})

server.listen(3000, () => {
  console.log("Terminal backend running on ws://localhost:3000")
})
