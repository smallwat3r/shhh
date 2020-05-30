export default function error_parser(data) {
  let msg = "";
  Object.values(data).forEach(value => (msg += value[0].replace(/.$/, " / ")));
  return msg.substring(0, msg.length - 2);
}
