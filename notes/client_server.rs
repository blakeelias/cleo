



pub fn server_thread() {
  let ledger = Ledger::new(config.ident, config.key)
  let socket = UdpSocket::new(LOCALHOST, 8000);
  let peers = BtreeMap<SockAddr, PeerInfo>
  loop { // assembing blocks
    let mut prev_block = &ledger.blocks.last_block()
    let mut curr_block = &ledger.blocks.new_block();
    let start = Instant::now();

    // Make push requests
    for peer in config.peers {
      match peer.type {
      BASIC => {
        socket.send_to(peer.addr, Request::new_basic_record_request())
      },
      BIDIR => else {
        socket.send_to(peer.addr, Request::new_basic_bidir_request(prev_block.hash))
      },
    }

    for (addr, info) in active_peers {
      socket.send_to(addr, Push(prev_block.hash)); 

    }


    sleep_until(Instant::now() + 1000/config.block_freq);
    Some((msg, addr)) = socket.recv_from(&buffer) {
      let mut record: Record ;
      match msg.request_type {
        FILE => {
           record = &block.new_file_entry();
           record.hash = File:open(msg.file_name).hash();
           record.file = msg.file_name;
        }
        BASIC => {
          ...
          // check record and insert
          block.insert(msg.record)
        }
        BIDIR => {
          // check record and insert
          ... 
        }
        BYTES => {
          block.hash = hash(msg.data(0))
          let f = File::new(&block.hash.to_string());
          record.hash = File:open(msg.file_name).hash();
          record.file = msg.file_name;

        } 
        PEERING => {
          peers.insert(Peer::new: {
              id:  msg.src,
              ttl: msg.ttl,
              service_type: msg.service_type
          });
        }
      }
    }
    block.time = tai_now();
    block.hash = hash(block.records);

  }
}


pub fn client_thread() {
  loop {
      let frame = camera.get_frame();
      ...

      //
      // socket.send_to(config.server, to_bytes)
      socket.send_to(config.server, Record::new_file_record(
            "filasdfasdf"))


  }

}
