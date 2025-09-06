import asyncio
import random
import secrets
from time import perf_counter


async def fetch_data(name: str, delay: float) -> dict:
    # Simulate I/O waiting for delay
    await asyncio.sleep(delay)
    data = secrets.token_hex(16)
    print(f"{name} ok in {delay:.1f}s")
    return {"data": data}


# ===============================
#            Basic tasks
# ===============================


async def basic_tasks():
    init = perf_counter()

    # Execute 3 concurrent tasks (single-thread, cooperative)
    results = await asyncio.gather(
        fetch_data("A", 1.0),
        fetch_data("B", 2.0),
        fetch_data("C", 1.5),
    )

    # Wait for all tasks to complete

    duration = perf_counter() - init
    print(results)
    for result in results:
        print(f"Received result: {result}")
    print(f"Total: {duration:.2f}s (should be ~2.0s, not 1.0+2.0+1.5)")


# ===============================
#            Task Groups
# ===============================


class TaskGroupExamples:
    """Demonstrates different usage scenarios of asyncio.TaskGroup."""

    @staticmethod
    async def basic_task_group():
        """Basic TaskGroup example with random names."""
        init = perf_counter()
        tasks = []

        async with asyncio.TaskGroup() as tg:
            # Create lists and shuffle randomly
            names = ["orange", "monkey", "banana", "house"]
            times = [1.0, 2.0, 1.5, 4.0]
            random.shuffle(names)

            for name, sleep_time in zip(names, times, strict=False):
                task = tg.create_task(fetch_data(name, sleep_time))
                tasks.append(task)

        results = [task.result() for task in tasks]
        print(f"📊 Results: {results}")
        for result in results:
            print(f"📋 Received result: {result}")

        duration = perf_counter() - init
        print(f"⏱️  Total: {duration:.2f}s (should be ~4.0s, not 1.0+2.0+1.5+4.0)")
        return results

    @staticmethod
    async def task_group_with_error_handling():
        """TaskGroup with error handling and exceptions."""
        init = perf_counter()
        print("\n🔄 TaskGroup with error handling...")

        async def fetch_with_retry(name: str, delay: float, fail_chance: float = 0.3):
            """Simulates fetch with possibility of failure."""
            await asyncio.sleep(delay)
            if random.random() < fail_chance:
                raise Exception(f"Simulated failure for {name}")
            return {"data": f"Success for {name}", "delay": delay}

        try:
            async with asyncio.TaskGroup() as tg:
                # Some tasks may fail
                tg.create_task(fetch_with_retry("A", 1.0, 0.1))
                tg.create_task(fetch_with_retry("B", 1.5, 0.5))
                tg.create_task(fetch_with_retry("C", 2.0, 0.2))
                tg.create_task(fetch_with_retry("D", 0.5, 0.8))

                print("🚀 Tasks created, waiting for completion...")

        except Exception as e:
            print(f"❌ Some task failed: {e}")

        duration = perf_counter() - init
        print(f"⏱️  Total time: {duration:.2f}s")
        return duration

    @staticmethod
    async def task_group_with_timeout():
        """TaskGroup with global timeout for all tasks."""
        init = perf_counter()
        print("\n⏰ TaskGroup with global timeout...")

        try:
            async with asyncio.timeout(2.5):  # Global timeout of 2.5s
                async with asyncio.TaskGroup() as tg:
                    # Tasks with different durations
                    tg.create_task(fetch_data("Fast", 0.5))
                    tg.create_task(fetch_data("Medium", 1.5))
                    tg.create_task(fetch_data("Slow", 3.0))  # Will fail due to timeout
                    tg.create_task(
                        fetch_data("Very Slow", 4.0),
                    )  # Will fail due to timeout

                    print("🚀 Tasks created with 2.5s timeout...")
                    await asyncio.sleep(0.1)  # Checkpoint for the cancellation scope

        except TimeoutError:
            print("⏰ Global timeout reached! Some tasks were cancelled.")

        duration = perf_counter() - init
        print(f"⏱️  Total time: {duration:.2f}s")
        return duration

    @staticmethod
    async def task_group_with_conditional_tasks():
        """TaskGroup that creates tasks conditionally based on results."""
        init = perf_counter()
        print("\n🎯 TaskGroup with conditional tasks...")

        async def check_condition(name: str) -> bool:
            """Simulates condition checking."""
            await asyncio.sleep(0.5)
            return random.choice([True, False])

        async def process_if_valid(name: str):
            """Processes only if condition is valid."""
            await asyncio.sleep(1.0)
            return f"Processed: {name}"

        results = []
        async with asyncio.TaskGroup() as tg:
            # First phase: check conditions
            condition_tasks = []
            for name in ["Item1", "Item2", "Item3", "Item4"]:
                task = tg.create_task(check_condition(name))
                condition_tasks.append((name, task))

            # Second phase: process only the valid ones
            process_tasks = []
            for name, condition_task in condition_tasks:
                is_valid = await condition_task
                if is_valid:
                    print(f"✅ {name} is valid, creating processing task...")
                    process_task = tg.create_task(process_if_valid(name))
                    process_tasks.append(process_task)
                else:
                    print(f"❌ {name} is not valid, skipping...")

            # Collect results
            for task in process_tasks:
                result = await task
                results.append(result)

        duration = perf_counter() - init
        print(f"📊 Final results: {results}")
        print(f"⏱️  Total time: {duration:.2f}s")
        return results

    @staticmethod
    async def task_group_with_resource_limiting():
        """TaskGroup with resource limiting (semaphore)."""
        init = perf_counter()
        print("\n🔒 TaskGroup with resource limiting...")

        # Semaphore limits to 2 simultaneous tasks
        semaphore = asyncio.Semaphore(2)

        async def fetch_with_semaphore(name: str, delay: float):
            """Fetch with resource control via semaphore."""
            async with semaphore:
                print(f"🔓 {name} acquired semaphore")
                await asyncio.sleep(delay)
                print(f"🔓 {name} released semaphore")
                return {"data": f"Data from {name}", "delay": delay}

        results = []
        async with asyncio.TaskGroup() as tg:
            # Create 6 tasks, but only 2 can run simultaneously
            for i in range(6):
                task = tg.create_task(
                    fetch_with_semaphore(f"Task{i + 1}", 1.0 + i * 0.2),
                )
                results.append(task)

            print("🚀 6 tasks created with semaphore limiting to 2 simultaneous...")

        # Collect results
        final_results = [task.result() for task in results]
        duration = perf_counter() - init
        print(f"📊 Results: {final_results}")
        print(f"⏱️  Total time: {duration:.2f}s")
        return final_results


async def task_groups():
    """Executes all TaskGroup examples."""
    print("🚀 DEMONSTRATING TASK GROUPS...")
    print("=" * 50)

    # Execute all examples
    await TaskGroupExamples.basic_task_group()
    await TaskGroupExamples.task_group_with_error_handling()
    await TaskGroupExamples.task_group_with_timeout()
    await TaskGroupExamples.task_group_with_conditional_tasks()
    await TaskGroupExamples.task_group_with_resource_limiting()

    print("=" * 50)
    print("✅ All TaskGroup examples completed!")


# ===============================
#            Future
# ===============================


class FutureSimulator:
    """Encapsulates asynchronous operations to resolve or fail a Future."""

    @staticmethod
    async def set_result(future: asyncio.Future, result: str):
        """Simulates an asynchronous operation that resolves a Future."""
        await asyncio.sleep(2)
        future.set_result(result)
        print(f"✅ Future resolved with result: '{result}'")

    @staticmethod
    async def set_exception(future: asyncio.Future, error_msg: str):
        """Simulates an operation that fails and sets an exception on the Future."""
        await asyncio.sleep(1.5)
        future.set_exception(Exception(error_msg))
        print(f"❌ Future failed with exception: '{error_msg}'")


class FutureDemoCases:
    """Encapsulates demonstrations of asyncio.Future usage."""

    @staticmethod
    async def demonstrate_basic_future_success(event_loop):
        """Demonstrates a basic Future resolved successfully."""
        print("\n📋 Case 1: Future with successful result")
        future_result = event_loop.create_future()
        resolve_task = event_loop.create_task(
            FutureSimulator.set_result(
                future_result,
                "Operation completed successfully!",
            ),
        )
        print(f"Task 1: {resolve_task}")

        try:
            result_value = await future_result
            print(f"🎯 Result received: {result_value}")
        except Exception as exc:
            print(f"❌ Unexpected error: {exc}")

    @staticmethod
    async def demonstrate_future_with_exception(event_loop):
        """Demonstrates a Future that ends with exception."""
        print("\n📋 Case 2: Future with failure/exception")
        future_result = event_loop.create_future()
        exception_task = event_loop.create_task(
            FutureSimulator.set_exception(
                future_result,
                "Database connection error",
            ),
        )
        print(f"Task 2: {exception_task}")

        try:
            result_value = await future_result
            print(f"🎯 Result received: {result_value}")
        except Exception as exc:
            print(f"❌ Exception caught: {exc}")

    @staticmethod
    async def demonstrate_future_with_timeout(event_loop):
        """Demonstrates a Future that exceeds the time limit (timeout)."""
        print("\n📋 Case 3: Future with timeout")
        future_result = event_loop.create_future()
        delayed_task = event_loop.create_task(
            FutureSimulator.set_result(future_result, "Late result"),
        )

        try:
            result_value = await asyncio.wait_for(future_result, timeout=1.0)
            print(f"🎯 Result received: {result_value}")
        except TimeoutError:
            print("⏰ Timeout! Future was not resolved in time")
            delayed_task.cancel()

    @staticmethod
    async def demonstrate_future_with_callback(event_loop):
        """Demonstrates a Future with completion callback."""
        print("\n📋 Case 4: Future with completion callback")
        future_result = event_loop.create_future()

        def on_future_done(completed_future):
            if completed_future.done():
                if completed_future.exception():
                    print(
                        f"🔔 Callback: Future failed with {completed_future.exception()}",
                    )
                else:
                    print(
                        f"🔔 Callback: Future completed with {completed_future.result()}",
                    )

        future_result.add_done_callback(on_future_done)
        callback_task = event_loop.create_task(
            FutureSimulator.set_result(future_result, "Future with callback!"),
        )
        print(f"Task 3: {callback_task}")
        await asyncio.sleep(0.1)

    @staticmethod
    async def demonstrate_multiple_futures_with_gather(event_loop):
        """Demonstrates multiple Futures resolved in parallel using gather."""
        print("\n📋 Case 5: Multiple Futures with gather")
        future_list = []
        for idx in range(3):
            future_result = event_loop.create_future()
            future_list.append(future_result)
            gather_task = event_loop.create_task(
                FutureSimulator.set_result(future_result, f"Result {idx + 1}"),
            )
            print(f"Task 4: {gather_task}")

        all_results = await asyncio.gather(*future_list, return_exceptions=True)
        print(f"🎯 All futures resolved: {all_results}")
        return all_results


async def main_future():
    """Demonstrates the benefits and use cases of Future."""
    init = perf_counter()
    print("🚀 Demonstrating Futures in asyncio...")
    print("=" * 50)

    loop = asyncio.get_running_loop()

    await FutureDemoCases.demonstrate_basic_future_success(loop)
    await FutureDemoCases.demonstrate_future_with_exception(loop)
    await FutureDemoCases.demonstrate_future_with_timeout(loop)
    await FutureDemoCases.demonstrate_future_with_callback(loop)
    results = await FutureDemoCases.demonstrate_multiple_futures_with_gather(loop)

    duration = perf_counter() - init
    print(f"\n⏱️  Total time: {duration:.2f}s")
    print("=" * 50)

    demonstrate_future_benefits()
    return results


def demonstrate_future_benefits():
    """Explains why to use Futures."""
    print("\n💡 BENEFITS OF FUTURES:")
    print("1. Manual control over when and how to resolve asynchronous operations")
    print("2. Ability to cancel operations in progress")
    print("3. Custom exception handling")
    print("4. Callbacks for automatic reactions when operations finish")
    print("5. Configurable timeouts")
    print("6. Composition of multiple asynchronous operations")
    print("7. Separation between creation and execution of operations")
    print("8. Useful for APIs that need granular control over operations")


# ===============================
#            Locks
# ===============================


class AsyncLockExamples:
    """Demonstrates different types of locks and synchronization in asyncio."""

    @staticmethod
    async def basic_lock_example():
        """Basic Lock example for exclusive access to a resource."""
        print("\n🔒 Basic Lock example...")

        # Shared resource
        shared_counter = 0
        lock = asyncio.Lock()

        async def increment_with_lock(name: str, delay: float):
            """Increments the counter with exclusive lock."""
            nonlocal shared_counter
            async with lock:
                print(f"🔓 {name} acquired the lock")
                current = shared_counter
                await asyncio.sleep(delay)  # Simulates work
                shared_counter = current + 1
                print(f"🔓 {name} released the lock, counter: {shared_counter}")

        # Execute multiple concurrent tasks
        async with asyncio.TaskGroup() as tg:
            tg.create_task(increment_with_lock("Task A", 0.5))
            tg.create_task(increment_with_lock("Task B", 0.3))
            tg.create_task(increment_with_lock("Task C", 0.7))
            tg.create_task(increment_with_lock("Task D", 0.2))

        print(f"📊 Final counter: {shared_counter}")
        return shared_counter

    @staticmethod
    async def rlock_example():
        """Example of RLock (Reentrant Lock) for recursive functions."""
        print("\n🔄 RLock (Reentrant Lock) example...")

        rlock = asyncio.Lock()  # asyncio.Lock is already reentrant

        async def recursive_function(name: str, depth: int):
            """Function that calls itself, demonstrating reentrancy."""
            async with rlock:
                print(f"🔓 {name} level {depth} - lock acquired")
                if depth > 0:
                    await asyncio.sleep(0.1)
                    await recursive_function(name, depth - 1)
                print(f"🔓 {name} level {depth} - lock released")

        async with asyncio.TaskGroup() as tg:
            tg.create_task(recursive_function("Task A", 3))
            tg.create_task(recursive_function("Task B", 2))

        print("✅ RLock demonstrated successfully!")

    @staticmethod
    async def semaphore_example():
        """Example of Semaphore to limit concurrency."""
        print("\n🚦 Semaphore example...")

        # Semaphore allows only 3 simultaneous tasks
        semaphore = asyncio.Semaphore(3)

        async def worker_with_semaphore(name: str, work_time: float):
            """Worker that uses semaphore to limit concurrency."""
            async with semaphore:
                print(
                    f"🚦 {name} acquired semaphore (available slots: {semaphore._value})",
                )
                await asyncio.sleep(work_time)
                print(f"🚦 {name} released semaphore")
                return f"Work by {name} completed"

        # Create 6 workers, but only 3 can run simultaneously
        tasks = []
        async with asyncio.TaskGroup() as tg:
            for idx in range(6):
                task = tg.create_task(
                    worker_with_semaphore(f"Worker{idx + 1}", 1.0 + idx * 0.2),
                )
                tasks.append(task)

        results = [task.result() for task in tasks]
        print(f"📊 Results: {results}")
        return results

    @staticmethod
    async def event_example():
        """Exemplo de Event para sincronização entre tasks."""
        print("\n🎯 Exemplo de Event...")

        # Event para sinalizar que uma condição foi atendida
        ready_event = asyncio.Event()
        results = []

        async def producer():
            """Producer que prepara dados e sinaliza quando pronto."""
            print("🏭 Producer iniciando preparação...")
            await asyncio.sleep(2.0)  # Simula preparação
            print("🏭 Producer sinalizando que está pronto!")
            ready_event.set()

        async def consumer(name: str):
            """Consumer que aguarda o producer estar pronto."""
            print(f"👤 {name} aguardando producer...")
            await ready_event.wait()
            print(f"👤 {name} recebeu sinal, processando...")
            await asyncio.sleep(0.5)
            results.append(f"Dados processados por {name}")

        async with asyncio.TaskGroup() as tg:
            tg.create_task(producer())
            tg.create_task(consumer("Consumer A"))
            tg.create_task(consumer("Consumer B"))
            tg.create_task(consumer("Consumer C"))

        print(f"📊 Resultados: {results}")
        return results

    @staticmethod
    async def condition_example():
        """Exemplo de Condition para sincronização complexa."""
        print("\n🔐 Exemplo de Condition...")

        # Condition para coordenar acesso a um buffer
        condition = asyncio.Condition()
        buffer: list[str] = []
        max_size = 3

        async def producer_condition(name: str):
            """Producer que aguarda espaço no buffer."""
            for idx in range(3):
                async with condition:
                    # Aguardar até ter espaço no buffer
                    while len(buffer) >= max_size:
                        print(f"🏭 {name} aguardando espaço no buffer...")
                        await condition.wait()

                    item = f"Item{idx} de {name}"
                    buffer.append(item)
                    print(f"🏭 {name} adicionou {item}, buffer: {buffer}")
                    condition.notify()  # Notificar consumers

                await asyncio.sleep(0.3)

        async def consumer_condition(name: str):
            """Consumer que aguarda itens no buffer."""
            for idx in range(3):
                async with condition:
                    # Aguardar até ter itens no buffer
                    while len(buffer) == 0:
                        print(f"👤 {name} aguardando itens no buffer...")
                        await condition.wait()

                    item = buffer.pop(0)
                    print(f"👤 {name} consumiu {item}, buffer: {buffer}")
                    condition.notify()  # Notificar producers

                await asyncio.sleep(0.4)

        async with asyncio.TaskGroup() as tg:
            tg.create_task(producer_condition("Producer A"))
            tg.create_task(consumer_condition("Consumer A"))

        print(f"📊 Buffer final: {buffer}")
        return buffer

    @staticmethod
    async def barrier_example():
        """Exemplo de Barrier para sincronização de múltiplas tasks."""
        print("\n🚧 Exemplo de Barrier...")

        # Barrier que aguarda 3 tasks chegarem
        barrier = asyncio.Barrier(3)

        async def worker_with_barrier(name: str, work_time: float):
            """Worker que aguarda todos chegarem na barrier."""
            print(f"👷 {name} iniciando trabalho...")
            await asyncio.sleep(work_time)
            print(f"👷 {name} chegou na barrier, aguardando outros...")

            try:
                await barrier.wait()
                print(f"🎉 {name} passou pela barrier! Todos chegaram!")
            except asyncio.BrokenBarrierError:
                print(f"❌ {name} - Barrier foi quebrada!")

        async with asyncio.TaskGroup() as tg:
            tg.create_task(worker_with_barrier("Worker A", 0.5))
            tg.create_task(worker_with_barrier("Worker B", 1.0))
            tg.create_task(worker_with_barrier("Worker C", 1.5))

        print("✅ Barrier concluída com sucesso!")

    @staticmethod
    async def queue_example():
        """Exemplo de Queue para comunicação entre tasks."""
        print("\n📦 Exemplo de Queue...")

        # Queue para comunicação producer-consumer
        queue: asyncio.Queue[str | None] = asyncio.Queue(maxsize=3)
        results = []

        async def producer_queue(name: str, items: int):
            """Producer que coloca itens na queue."""
            for i in range(items):
                item = f"Item{i} de {name}"
                await queue.put(item)
                print(f"🏭 {name} colocou {item} na queue (tamanho: {queue.qsize()})")
                await asyncio.sleep(0.2)

            # Sinalizar fim
            await queue.put(None)
            print(f"🏭 {name} finalizou")

        async def consumer_queue(name: str):
            """Consumer que retira itens da queue."""
            while True:
                item = await queue.get()
                if item is None:
                    queue.task_done()
                    break

                print(f"👤 {name} consumiu {item}")
                await asyncio.sleep(0.3)
                results.append(f"{name} processou {item}")
                queue.task_done()

            print(f"👤 {name} finalizou")

        async with asyncio.TaskGroup() as tg:
            tg.create_task(producer_queue("Producer A", 2))
            tg.create_task(consumer_queue("Consumer A"))

        # Aguardar todas as tasks terminarem
        await queue.join()
        print(f"📊 Resultados: {results}")
        return results


async def demonstrate_locks():
    """Executa todos os exemplos de locks e sincronização."""
    print("🔒 DEMONSTRANDO LOCKS E SINCRONIZAÇÃO EM ASYNCIO...")
    print("=" * 60)

    # Executar todos os exemplos
    await AsyncLockExamples.basic_lock_example()
    await AsyncLockExamples.rlock_example()
    await AsyncLockExamples.semaphore_example()
    await AsyncLockExamples.event_example()
    await AsyncLockExamples.condition_example()
    await AsyncLockExamples.barrier_example()
    await AsyncLockExamples.queue_example()

    print("=" * 60)
    print("✅ Todos os exemplos de locks concluídos!")


if __name__ == "__main__":
    # Executar demonstração dos TaskGroups
    print("🎯 EXECUTANDO EXEMPLOS DE TASK GROUPS...")
    asyncio.run(task_groups())

    print("\n" + "=" * 60 + "\n")

    # Executar demonstração dos Futures
    print("🎯 EXECUTANDO EXEMPLOS DE FUTURES...")
    asyncio.run(main_future())

    print("\n" + "=" * 60 + "\n")

    # Executar demonstração dos Locks
    print("🎯 EXECUTANDO EXEMPLOS DE LOCKS...")
    asyncio.run(demonstrate_locks())
