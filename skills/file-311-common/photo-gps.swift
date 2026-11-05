import CoreGraphics
import Foundation
import ImageIO

let path = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : ""
let url = URL(fileURLWithPath: path)
guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
      let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [CFString: Any],
      let gps = props[kCGImagePropertyGPSDictionary] as? [CFString: Any],
      let lat = gps[kCGImagePropertyGPSLatitude] as? Double,
      let lon = gps[kCGImagePropertyGPSLongitude] as? Double
else {
    fputs("This photo has no location.\n", stderr)
    exit(2)
}

var latitude = lat
var longitude = lon
if (gps[kCGImagePropertyGPSLatitudeRef] as? String) == "S" { latitude = -latitude }
if (gps[kCGImagePropertyGPSLongitudeRef] as? String) == "W" { longitude = -longitude }
print("\(latitude) \(longitude)")
