### v0.2.0 - Real WebRTC Implementation
- Backend: FastAPI signaling server with in-memory session store
  - POST /api/session — creates 4-char session code
  - PUT/GET /api/session/{code}/offer — SDP offer exchange
  - PUT/GET /api/session/{code}/answer — SDP answer exchange
  - POST/GET /api/session/{code}/ice/{sender|receiver} — ICE candidate relay
  - Sessions expire after 10 minutes, auto-cleaned on new session creation
- Frontend: replaced all fake/simulated transfer code with real WebRTC
  - Sender creates RTCPeerConnection + DataChannel, posts offer to signaling server
  - Sender polls for answer SDP, then polls for receiver ICE candidates
  - Receiver fetches offer, creates answer, both sides exchange ICE via server
  - Files transferred as 64KB ArrayBuffer chunks over RTCDataChannel with backpressure
  - Receiver reassembles chunks into Blob and triggers browser download for each file
  - Progress bars now reflect actual transfer, not a timer simulation
  - Configure SIGNALING_SERVER constant at top of script for production deployment

### v0.1.0 - Initial Blueprint
- Project initialized
