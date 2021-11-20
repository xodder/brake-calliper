def get_triangles(filepath):
  triangles = []
  vertices = []
  normals = []
  with open(filepath, 'r') as file:
    for line in file:
      if line.startswith('v '):
        values = line.split(' ')[1:]
        values = list(map(lambda value: value.strip(), values))
        vertices.append((values[0], values[1], values[2]))
      elif line.startswith('vn'):
        values = line.split(' ')[1:]
        values = list(map(lambda value: value.strip(), values))
        normals.append((values[0], values[1], values[2]))
      elif line.startswith('f '):
        values = line.split(' ')[1:]
        values = list(map(lambda value: value.split('/'), values))
        triangle = {'positions': [], 'normals': []}

        for value in values:
          [vertex_index, _, normal_index] = value
          triangle['positions'].append(vertices[int(vertex_index) - 1])
          triangle['normals'].append(normals[int(normal_index) - 1])

        triangles.append(triangle)

  return triangles


def generate_pyglet_code_from_triangles(triangles):
  code = ''
  code += 'batch = pyglet.graphics.Batch()'
  code += '\n'

  for triangle in triangles:
    positions = ','.join([','.join(position) for position in triangle['positions']])
    positions = '(\'v3f\', ({}))'.format(positions)

    normals = ','.join([','.join(normal) for normal in triangle['normals']])
    normals = '(\'n3f\', ({}))'.format(normals)

    code += 'batch.add(3, GL_TRIANGLES, None, {}, {})'.format(positions, normals)
    code += '\n'

  return code


def generate_gl_code_triangles(triangles):
  code = ''
  code += 'def get_vertices():'
  code += '\n\t'
  code += 'return ['
  code += '\n\t\t'

  count = 0

  for triangle in triangles:
    for i in range(len(triangle['positions'])):
      position = triangle['positions'][i]
      normal = triangle['normals'][i]
      code += ','.join(position)
      code += ','
      code += ','.join(normal)
      code += ','
      code += '\n\t\t'
      count += 1

  code += ']'
  code += '\n' * 2
  code += 'def get_vertices_count():'
  code += '\n\t'
  code += 'return {}'.format(count)
  code += '\n'

  return code


def convert_obj_to_pyglet(source, destination):
  triangles = get_triangles(source)
  generated_code = generate_pyglet_code_from_triangles(triangles)

  try:
    fp = open(destination, 'w')
    fp.write(generated_code)
    fp.close()
  except FileNotFoundError:
    print('destination file not found')
  except IOError:
    print('error occurred while writing to file')


def convert_obj_to_glcode(source, destination):
  triangles = get_triangles(source)
  generated_code = generate_gl_code_triangles(triangles)

  try:
    fp = open(destination, 'w')
    fp.write(generated_code)
    fp.close()
  except FileNotFoundError:
    print('destination file not found')
  except IOError:
    print('error occurred while writing to file')


if __name__ == '__main__':
  convert_obj_to_glcode('model/raw/caliper.obj', 'model/raw/caliper_alt.py')
